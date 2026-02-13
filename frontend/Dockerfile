# Stage 1: Build
FROM node:22-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
# Set environment variables for build if needed
# ARG VITE_API_BASE_URL
# ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2: Serve
FROM nginxinc/nginx-unprivileged:alpine

# Copy build artifacts
COPY --from=build /app/dist /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# The unprivileged image listens on 8080 by default, matching our config
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
