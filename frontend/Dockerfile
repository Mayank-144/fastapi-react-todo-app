# 1. Base Image: Node.js 20 Alpine Linux
FROM node:20-alpine

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# 4. Copy frontend source code
COPY . .

# 5. Expose Vite port
EXPOSE 5173

# 6. Start Vite dev server with host binding
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
