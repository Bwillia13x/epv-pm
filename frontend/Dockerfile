# ---- Builder Stage ----
FROM node:20-alpine AS builder
WORKDIR /app

# Install deps
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --prod=false

# Copy source and build
COPY . .
RUN pnpm build

# ---- Production Stage ----
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Install production deps
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile --prod

# Copy built assets
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

CMD ["pnpm", "start"] 