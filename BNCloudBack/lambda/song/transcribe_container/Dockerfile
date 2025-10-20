FROM public.ecr.aws/lambda/python:3.11

# Install curl and xz to fetch static ffmpeg build
RUN yum -y install tar xz curl && \
    curl -L -o /tmp/ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    mkdir -p /opt/ffmpeg && \
    tar -xJf /tmp/ffmpeg.tar.xz -C /opt/ffmpeg --strip-components=1 && \
    ln -s /opt/ffmpeg/ffmpeg /usr/local/bin/ffmpeg && \
    ln -s /opt/ffmpeg/ffprobe /usr/local/bin/ffprobe && \
    rm -rf /var/cache/yum/* /tmp/*

# Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -t /var/task

# Copy handler
COPY handler.py ${LAMBDA_TASK_ROOT}/handler.py

# Set the Lambda handler entrypoint
CMD ["handler.transcribe"]

