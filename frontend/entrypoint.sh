#!/bin/sh

# Create .env.development.local with environment variables
echo "NEXT_PUBLIC_API_URI=${NEXT_PUBLIC_API_URI}/data" > .env.development.local
echo "NEXT_PUBLIC_feed_URI=${NEXT_PUBLIC_FEED_URI}/feed" >> .env.development.local
echo "NEXT_PUBLIC_image_server_URI=${NEXT_PUBLIC_image_server_URI}/images" >> .env.development.local

# Run the original command
exec "$@"