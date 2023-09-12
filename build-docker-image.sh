DOCKERFILE="Dockerfile"
ORG="enoriega"
IMAGE_NAME="AZX"
docker buildx build --output=type=docker --platform linux/amd64 -f ${DOCKERFILE} -t "${ORG}/${IMAGE_NAME}:latest" -t "${ORG}/${IMAGE_NAME}:amd64" .