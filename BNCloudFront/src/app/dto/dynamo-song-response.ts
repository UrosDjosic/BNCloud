export interface DynamoSongResponse {
  songId: string,
  audioUploadUrl: string,
  imageUploadUrl: string,
  s3Bucket: string,
  audioKey: string,
  imageKey: string
}
