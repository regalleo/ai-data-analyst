#!/bin/bash
# Deployment script for Vercel frontend

echo "=== Deploying frontend to Vercel ==="
cd /Users/rajshekharsingh/Desktop/ai-data-analyst/frontend

echo "Installing dependencies..."
npm install

echo "Building Next.js app..."
npm run build

echo "Deploying to Vercel..."
npx vercel --prod --yes

echo "=== Deployment complete ==="

