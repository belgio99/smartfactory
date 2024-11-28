# Step 1: Use an official Node.js image as the base image
FROM node:18-alpine AS builder

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Install project dependencies
# Copy package.json and package-lock.json (or yarn.lock) for better caching of dependencies
COPY package.json package-lock.json ./

# Install dependencies using npm
RUN npm install

# Step 4: Copy the rest of the application code into the container
COPY . .

# Step 5: Build the React app (TypeScript compilation included)
RUN npm run build

# Step 6: Use a smaller web server (like Nginx) to serve the built app
FROM nginx:alpine

# Step 7: Copy the built React app to Nginx's web directory
COPY --from=builder /app/build /usr/share/nginx/html

# Step 8: Expose the port that Nginx is serving the app on
EXPOSE 8000

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Step 9: Use Nginx to serve the app
CMD ["nginx", "-g", "daemon off;"]
