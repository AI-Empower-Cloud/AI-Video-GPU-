#!/bin/sh

# Start nginx in background
nginx -g "daemon off;" &

# Start the Vue.js application
npm run serve

# Keep the container running
wait
