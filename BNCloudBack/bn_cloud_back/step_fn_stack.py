from aws_cdk import (
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sqs as sqs,
    Stack,
    Duration
)
from constructs import Construct


class StepFunctionStack(Stack):
    def __init__(self, scope: Construct,id: str,feed_queue: sqs.Queue,tables, **kwargs):
        super().__init__(scope, id, **kwargs)
        #Define tasks!

        #After every heuristic calculation in any of starter lambdas, we call update FeedScores table
        update_feed_scores_lambda = _lambda.Function(
            self, "FeedScoresUpdateLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="step_fn.score_update.handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "FEED_TABLE": tables['feed_scores'].table_name
            }
        )
        feed_scores_table = tables['feed_scores']
        feed_scores_table.grant_read_write_data(update_feed_scores_lambda)

        update_feed_scores_task = tasks.LambdaInvoke(
            self, "UpdateFeedScoresTask",
            lambda_function=update_feed_scores_lambda,
            output_path="$.Payload"
        )


        #After updating FeedScores Table, we can query and get max scores for songs, genres, artists!
        update_user_feed_lambda = _lambda.Function(
            self, "UserFeedUpdateLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="step_fn.feed_update.handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "FEED_SCORES_TABLE": tables["feed_scores"].table_name,
                "USER_FEED_TABLE": tables["users_feed"].table_name
            }
        )
        feed_scores_table.grant_read_data(update_user_feed_lambda)
        tables["users_feed"].grant_read_write_data(update_user_feed_lambda)
        update_user_feed_task = tasks.LambdaInvoke(
            self, "UpdateUserFeedTask",
            lambda_function=update_user_feed_lambda,
            output_path="$.Payload"
        )
        def make_chain(base_lambda_id: str, handler_path: str):
            base_task = tasks.LambdaInvoke(
                self, f"{base_lambda_id}Task",
                lambda_function=_lambda.Function(
                    self, f"{base_lambda_id}Lambda",
                    runtime=_lambda.Runtime.PYTHON_3_11,
                    handler=handler_path,
                    code=_lambda.Code.from_asset("lambda")
                ),
                output_path="$.Payload"
            )
            # Create unique tasks per branch
            update_feed_scores = tasks.LambdaInvoke(
                self, f"UpdateFeedScoresTask_{base_lambda_id}",
                lambda_function=update_feed_scores_lambda,
                output_path="$.Payload"
            )
            update_user_feed = tasks.LambdaInvoke(
                self, f"UpdateUserFeedTask_{base_lambda_id}",
                lambda_function=update_user_feed_lambda,
                output_path="$.Payload"
            )
            return base_task.next(update_feed_scores).next(update_user_feed)
        rate_song_chain = make_chain("UserRatedSong", "step_fn.user_rated.handler.rated")
        subscribe_chain = make_chain("UserSubscribed", "step_fn.user_subscribed.handler.subscribed")
        listening_chain = make_chain("UserListening", "step_fn.user_listened.handler.listened")

        # Step Function router (Choice)
        choice = sfn.Choice(self, "WhatEvent?")
        choice.when(sfn.Condition.string_equals("$.event_type", "user_rated_song"), rate_song_chain)
        choice.when(sfn.Condition.string_equals("$.event_type", "user_subscribed"), subscribe_chain)
        choice.when(sfn.Condition.string_equals("$.event_type", "user_listening"), listening_chain)
        choice.otherwise(sfn.Fail(self, "UnknownEvent"))


        # Create the state machine
        self.state_machine = sfn.StateMachine(
            self, "UpdateFeedWorkflow",
            definition_body=sfn.DefinitionBody.from_chainable(choice),
            timeout=Duration.minutes(5)
        )
        #SQS STACK -> CONSUMER LAMBDA -> STEP FUNCTION
        consumer_lambda = _lambda.Function(
            self, "SqsConsumerFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="step_fn.invoke_step_fn.handler.invoke",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "STATE_MACHINE_ARN": self.state_machine.state_machine_arn
            }
            
        )

        self.state_machine.grant_start_execution(consumer_lambda)

        consumer_lambda.add_event_source(lambda_event_sources.SqsEventSource(feed_queue))
