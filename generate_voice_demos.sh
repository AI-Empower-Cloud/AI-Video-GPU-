#!/bin/bash

# Voice Demo Generator for AI Video GPU Platform
# Demonstrates all available voice types with sample videos

echo "🎙️ AI Video GPU - Voice Types Demo Generator"
echo "============================================="

# Create demo directory
mkdir -p voice_demos
cd voice_demos

echo "📁 Creating voice demo samples..."

# Demo texts for different voice types
MALE_TEXT="Welcome to our comprehensive business presentation. Today we'll explore innovative solutions that drive growth and success."

FEMALE_TEXT="Take a moment to breathe deeply and find your inner peace. Let's begin this guided meditation journey together."

CHILD_TEXT="Hi everyone! Let's explore the amazing world of science together. Did you know that rainbows have seven colors?"

NARRATOR_TEXT="In a land far away, where dragons soared through misty mountains, an extraordinary adventure was about to begin."

MULTILINGUAL_TEXT="Bonjour mes amis! Heute lernen wir zusammen. ¡Vamos a crear algo increíble!"

echo "🎬 Generating demo videos for each voice type..."

# 1. Professional Male Voice Demo
echo "Creating professional male voice demo..."
python ../main.py generate "$MALE_TEXT" \
  --tts-backend tortoise \
  --voice-name tom \
  --background-prompt "modern corporate office boardroom" \
  --visual-style professional \
  --output professional_male_demo.mp4

# 2. Warm Female Voice Demo  
echo "Creating warm female voice demo..."
python ../main.py generate "$FEMALE_TEXT" \
  --tts-backend tortoise \
  --voice-name angie \
  --background-prompt "peaceful meditation garden sunset" \
  --visual-style serene \
  --output meditation_female_demo.mp4

# 3. Educational Content with Child-like Voice
echo "Creating educational child voice demo..."
python ../main.py generate "$CHILD_TEXT" \
  --tts-backend xtts \
  --background-prompt "colorful science classroom with experiments" \
  --visual-style animated educational \
  --output educational_child_demo.mp4

# 4. Storytelling Narrator Voice
echo "Creating storytelling narrator demo..."
python ../main.py generate "$NARRATOR_TEXT" \
  --tts-backend tortoise \
  --voice-name freeman \
  --background-prompt "mystical fantasy landscape with dragons" \
  --visual-style cinematic fantasy \
  --output storytelling_narrator_demo.mp4

# 5. Multiple Voice Types in One Scene
echo "Creating multi-voice conversation demo..."

# Create conversation script
cat > conversation_script.json << 'EOF'
[
  {
    "speaker": "narrator",
    "text": "Our story begins with three friends meeting for the first time.",
    "voice_type": "male_narrator",
    "avatar": "narrator.jpg"
  },
  {
    "speaker": "sarah", 
    "text": "Hello everyone! I'm so excited to be here today.",
    "voice_type": "female_friendly",
    "avatar": "female_character.jpg"
  },
  {
    "speaker": "mike",
    "text": "Great to meet you Sarah! This is going to be an amazing project.",
    "voice_type": "male_professional", 
    "avatar": "male_character.jpg"
  },
  {
    "speaker": "emma",
    "text": "Can I help too? I have lots of creative ideas!",
    "voice_type": "child_enthusiastic",
    "avatar": "child_character.jpg"
  }
]
EOF

python ../main.py batch conversation_script.json \
  --output-dir multi_voice_conversation/ \
  --max-parallel 2

# 6. Voice Emotion Demonstrations
echo "Creating voice emotion demos..."

# Happy emotion
python ../main.py generate "This is fantastic news! I'm absolutely thrilled to share this with you!" \
  --tts-backend xtts \
  --emotion happy \
  --background-prompt "bright celebration party" \
  --output happy_emotion_demo.mp4

# Calm emotion  
python ../main.py generate "Let's take things slowly and methodically. There's no need to rush." \
  --tts-backend xtts \
  --emotion calm \
  --background-prompt "peaceful zen garden" \
  --output calm_emotion_demo.mp4

# Excited emotion
python ../main.py generate "This is incredible! You won't believe what we've discovered!" \
  --tts-backend xtts \
  --emotion excited \
  --background-prompt "amazing scientific laboratory" \
  --output excited_emotion_demo.mp4

# 7. Multilingual Voice Demo
echo "Creating multilingual voice demo..."

# English
python ../main.py generate "Welcome to our international presentation." \
  --language en \
  --output multilingual_english.mp4

# Spanish  
python ../main.py generate "Bienvenidos a nuestra presentación internacional." \
  --language es \
  --output multilingual_spanish.mp4

# French
python ../main.py generate "Bienvenue à notre présentation internationale." \
  --language fr \
  --output multilingual_french.mp4

# 8. Voice Speed Variations
echo "Creating voice speed variation demos..."

# Slow and deliberate
python ../main.py generate "This is important information that requires careful consideration." \
  --speed 0.8 \
  --background-prompt "serious business meeting" \
  --output slow_deliberate_demo.mp4

# Fast and energetic
python ../main.py generate "Quick update! Here are the latest exciting developments!" \
  --speed 1.3 \
  --background-prompt "dynamic newsroom" \
  --output fast_energetic_demo.mp4

# 9. Age-Appropriate Voice Demos
echo "Creating age-appropriate voice demos..."

# Elderly wisdom voice (using slow, deep settings)
python ../main.py generate "In my many years of experience, I have learned that patience and wisdom go hand in hand." \
  --speed 0.85 \
  --background-prompt "wise elder in library" \
  --output elderly_wisdom_demo.mp4

# Young adult voice (energetic, modern)
python ../main.py generate "Hey everyone! Check out this awesome new technology that's changing everything!" \
  --speed 1.1 \
  --background-prompt "modern tech startup office" \
  --output young_adult_demo.mp4

# 10. Professional Use Case Demos
echo "Creating professional use case demos..."

# Medical/Healthcare
python ../main.py generate "Today we'll discuss the latest advances in medical treatment and patient care protocols." \
  --tts-backend tortoise \
  --voice-name professional_female \
  --background-prompt "modern medical facility" \
  --visual-style medical professional \
  --output medical_professional_demo.mp4

# Legal/Government
python ../main.py generate "This policy briefing covers the essential regulatory changes and compliance requirements." \
  --tts-backend tortoise \
  --voice-name professional_male \
  --background-prompt "government office or courthouse" \
  --visual-style authoritative \
  --output legal_government_demo.mp4

# Educational/Academic
python ../main.py generate "Welcome to today's lecture on advanced quantum physics and its practical applications." \
  --tts-backend tortoise \
  --voice-name academic \
  --background-prompt "university lecture hall" \
  --visual-style academic \
  --output academic_lecture_demo.mp4

echo ""
echo "🎉 Voice Demo Generation Complete!"
echo "=================================="
echo ""
echo "📁 Generated demo files:"
echo "   • professional_male_demo.mp4 - Business presentation"
echo "   • meditation_female_demo.mp4 - Wellness content"  
echo "   • educational_child_demo.mp4 - Kids educational"
echo "   • storytelling_narrator_demo.mp4 - Fantasy narration"
echo "   • multi_voice_conversation/ - Multiple character dialogue"
echo "   • *_emotion_demo.mp4 - Various emotional styles"
echo "   • multilingual_*.mp4 - Different languages"
echo "   • *_speed_demo.mp4 - Speed variations"
echo "   • *_age_demo.mp4 - Age-appropriate voices"
echo "   • *_professional_demo.mp4 - Industry-specific"
echo ""
echo "🎭 Voice Types Demonstrated:"
echo "   ✅ Male voices (professional, narrator, casual)"
echo "   ✅ Female voices (warm, professional, energetic)"  
echo "   ✅ Child-appropriate voices (educational, enthusiastic)"
echo "   ✅ Elderly voices (wise, experienced)"
echo "   ✅ Emotional variations (happy, calm, excited)"
echo "   ✅ Speed variations (slow deliberate, fast energetic)"
echo "   ✅ Multilingual capabilities (English, Spanish, French)"
echo "   ✅ Professional contexts (medical, legal, academic)"
echo ""
echo "🚀 Next Steps:"
echo "   1. Review the generated demo videos"
echo "   2. Choose your preferred voice types"
echo "   3. Clone custom voices using your own samples"
echo "   4. Create production-ready content"
echo ""
echo "💡 Voice Cloning Quick Start:"
echo "   python ../main.py clone-voice sample1.wav sample2.wav \\"
echo "     --output custom_voice --name my_voice --backend xtts"
echo ""
echo "🎬 Your AI Video GPU platform supports ALL voice types!"
echo "Ready for professional video production! 🚀"
