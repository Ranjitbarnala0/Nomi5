#!/bin/bash
echo "🚀 Starting Project Nomi APK Build..."

# Check if logged in, if not, login
echo "Checking Expo Login Status..."
npx eas whoami
if [ $? -ne 0 ]; then
    echo "⚠️  You are not logged in."
    echo "👉 Please log in to your Expo account now:"
    npx eas login
fi

# Run the build
echo "🏗️  Starting Android APK Build (Preview Profile)..."
npx eas build -p android --profile preview

echo "✅ Build process initiated! Once finished, you will see a download link."
