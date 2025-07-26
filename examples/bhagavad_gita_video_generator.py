#!/usr/bin/env python3
"""
Bhagavad Gita Video Generator
Creates contemplative videos with Sanskrit verses, explanations, and real-world applications
Focus on making ancient wisdom applicable to modern life situations
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

try:
    from pipeline import VideoPipeline
    from config import load_config
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BhagavadGitaVideoGenerator:
    """Generator for Bhagavad Gita contemplative videos"""
    
    def __init__(self):
        """Initialize the Bhagavad Gita video generator"""
        self.pipeline = None
        self.config = None
        self.gita_database = self.load_gita_verses()
        self.setup_pipeline()
    
    def load_gita_verses(self) -> Dict[str, Any]:
        """Load comprehensive Bhagavad Gita verse database"""
        
        # Comprehensive database of key Bhagavad Gita verses
        verses = {
            "2.47": {
                "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
                "pronunciation": "Karmaṇy-evādhikāras te mā phaleṣu kadācana, Mā karma-phala-hetur bhūr mā te saṅgo 'stv akarmaṇi",
                "translation": "You have a right to perform your prescribed duty, but do not hanker after the results. Do not consider yourself the cause of the results, nor be attached to inaction.",
                "theme": "Karma Yoga - Action without attachment",
                "life_applications": [
                    {
                        "situation": "Work and Career Stress",
                        "explanation": "Focus on doing your best work without obsessing over promotions, recognition, or outcomes",
                        "practice": "Each day, identify one task where you can practice detached action - giving your full effort while releasing attachment to specific results",
                        "real_example": "A software developer writes clean, well-tested code not for praise, but because it's the right thing to do. When bugs arise, they fix them without self-blame."
                    },
                    {
                        "situation": "Parenting Challenges",
                        "explanation": "Guide and teach your children with love, but allow them to make their own choices and learn from consequences",
                        "practice": "When giving advice or setting boundaries, ask yourself: 'Am I doing this for their growth or my own need to control outcomes?'",
                        "real_example": "A parent teaches their teenager about responsible spending, then allows them to manage their allowance and learn from their financial decisions."
                    },
                    {
                        "situation": "Relationship Conflicts", 
                        "explanation": "Express your truth and feelings honestly, but don't manipulate to get specific responses",
                        "practice": "Before difficult conversations, remind yourself: 'I will speak my truth lovingly and let them respond authentically'",
                        "real_example": "In an argument with a spouse, focus on expressing your feelings clearly rather than trying to make them apologize or change immediately."
                    }
                ],
                "daily_practices": [
                    "Morning intention: Choose one task today to practice detached action",
                    "Evening reflection: Where did I act from attachment vs. duty today?",
                    "Weekly review: What results am I overly attached to this week?"
                ],
                "contemplation_questions": [
                    "What would I do differently if I truly didn't care about others' opinions?",
                    "How does attachment to outcomes create suffering in my life?",
                    "What is my dharma (righteous duty) in this situation?"
                ]
            },
            
            "6.5": {
                "sanskrit": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्। आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
                "pronunciation": "Uddhared ātmanātmānaṁ nātmānam avasādayet, Ātmaiva hy ātmano bandhur ātmaiva ripur ātmanaḥ",
                "translation": "One must elevate oneself by one's own mind, not degrade oneself. The mind is the friend of the conditioned soul, and his enemy as well.",
                "theme": "Self-Mastery and Mental Discipline",
                "life_applications": [
                    {
                        "situation": "Dealing with Failure or Setbacks",
                        "explanation": "After failure, choose to learn and grow (mind as friend) rather than fall into self-criticism (mind as enemy)",
                        "practice": "When facing setbacks, immediately ask: 'What can I learn?' instead of 'Why me?' Transform victim mindset to growth mindset",
                        "real_example": "After losing a job, instead of spiral into self-doubt, you analyze what skills to develop and see it as redirection toward better opportunities."
                    },
                    {
                        "situation": "Morning Routine and Self-Discipline",
                        "explanation": "Your mind can encourage healthy habits or make excuses. Choose which voice to follow",
                        "practice": "Each morning, consciously choose thoughts that serve your highest good. Replace 'I don't feel like it' with 'This aligns with my values'",
                        "real_example": "When the alarm goes off for morning exercise, instead of hitting snooze, you think: 'My body and mind will thank me for this investment in myself.'"
                    },
                    {
                        "situation": "Dealing with Criticism",
                        "explanation": "External criticism only has power if your internal critic amplifies it. A disciplined mind extracts wisdom while maintaining peace",
                        "practice": "When receiving criticism, pause and ask: 'Is there truth I can learn from this?' Separate feedback from emotional charge",
                        "real_example": "When your boss criticizes your presentation, instead of defensive anger, you think: 'What valid points can help me improve?' while maintaining self-worth."
                    }
                ],
                "daily_practices": [
                    "Monitor internal dialogue - replace one negative thought daily with a constructive one",
                    "Evening journaling: How did I choose to be my own friend vs. enemy today?",
                    "Morning affirmation: 'I choose thoughts that elevate and empower me'"
                ],
                "contemplation_questions": [
                    "In what ways do I currently act as my own worst enemy?",
                    "How can I become a better friend to myself?",
                    "What mental habits would serve my highest potential?"
                ]
            },
            
            "2.62": {
                "sanskrit": "ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते। सङ्गात्सञ्जायते कामः कामात्क्रोधोऽभिजायते॥",
                "pronunciation": "Dhyāyato viṣayān puṁsaḥ saṅgas teṣūpajāyate, Saṅgāt sañjāyate kāmaḥ kāmāt krodho 'bhijāyate",
                "translation": "While contemplating objects of the senses, attachment develops. From attachment comes desire, and from desire anger arises.",
                "theme": "Understanding the Chain of Mental Suffering",
                "life_applications": [
                    {
                        "situation": "Social Media and Comparison",
                        "explanation": "Constantly viewing others' highlight reels creates attachment to having what they have, leading to dissatisfaction",
                        "practice": "Before opening social media, set an intention: 'I view this for connection, not comparison.' Notice when comparison thoughts arise",
                        "real_example": "Seeing a friend's vacation photos, instead of feeling inadequate about your staycation, you feel genuine happiness for their joy."
                    },
                    {
                        "situation": "Consumer Desires and Shopping",
                        "explanation": "Dwelling on wanting material things creates attachment, then frustration when we can't have them immediately",
                        "practice": "Practice the 24-hour rule: wait a day before any non-essential purchase. Notice how desire often naturally diminishes",
                        "real_example": "Seeing an expensive gadget ad, you bookmark it instead of buying immediately. Often, you forget about it within days."
                    },
                    {
                        "situation": "Workplace Jealousy",
                        "explanation": "Focusing on others' promotions or recognition breeds attachment to getting the same, then anger when overlooked",
                        "practice": "When noticing workplace jealousy, redirect focus to your own growth and contribution rather than comparing achievements",
                        "real_example": "A colleague gets promoted. Instead of resentment, you congratulate them genuinely and ask for advice on your own development."
                    }
                ],
                "daily_practices": [
                    "Mindful consumption: Notice what media/content you're feeding your mind",
                    "Gratitude practice: Daily appreciation for what you already have",
                    "Desire awareness: When wanting something, trace the thought chain back to its origin"
                ],
                "contemplation_questions": [
                    "What am I dwelling on that creates unnecessary suffering?",
                    "How can I enjoy life's pleasures without becoming attached?",
                    "What desires am I feeding through my attention and thoughts?"
                ]
            },
            
            "18.66": {
                "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज। अहं त्वा सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
                "pronunciation": "Sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja, Ahaṁ tvā sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ",
                "translation": "Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
                "theme": "Surrender and Trust in Life's Intelligence",
                "life_applications": [
                    {
                        "situation": "Career Uncertainty and Life Transitions",
                        "explanation": "Sometimes we must let go of rigid life plans and trust that life has intelligence beyond our limited perspective",
                        "practice": "When facing major uncertainty, practice saying: 'I've done my part, now I trust the process.' Take action without forcing outcomes",
                        "real_example": "After a layoff, instead of desperate job searching, you trust that this transition may lead to better opportunities while taking practical steps."
                    },
                    {
                        "situation": "Health Challenges",
                        "explanation": "Surrender doesn't mean giving up, but doing your best while accepting that some things are beyond your control",
                        "practice": "With health issues, focus fully on what you can control (treatment, lifestyle) while surrendering anxiety about what you cannot",
                        "real_example": "Facing a health diagnosis, you research treatments and follow medical advice while releasing obsessive worry about outcomes."
                    },
                    {
                        "situation": "Relationship Troubles",
                        "explanation": "After honest communication and effort, sometimes we must surrender the need to control another person's choices",
                        "practice": "In relationship conflicts, express your truth clearly, then release attachment to how the other person responds",
                        "real_example": "After expressing your needs in a friendship, you let go of trying to change them and allow the relationship to evolve naturally."
                    }
                ],
                "daily_practices": [
                    "Morning surrender: 'I will do my best today and trust the results to life's wisdom'",
                    "Evening release: Let go of the day's unfinished business and unmet expectations",
                    "Weekly reflection: Where am I trying to control what's beyond my influence?"
                ],
                "contemplation_questions": [
                    "What am I trying to control that would be better surrendered?",
                    "How can I act with full effort while holding outcomes lightly?",
                    "What would I do if I truly trusted life's intelligence?"
                ]
            }
        }
        
        return verses
    
    def setup_pipeline(self):
        """Setup video generation pipeline optimized for contemplative content"""
        try:
            if not PIPELINE_AVAILABLE:
                logger.error("❌ Pipeline not available. Please run setup first.")
                return False
            
            # Load base configuration
            self.config = load_config("config/default.yaml")
            
            # Override settings for contemplative spiritual videos
            self.config.update({
                'video': {
                    'duration': 300,  # 5 minutes for deep contemplation
                    'fps': 24,
                    'resolution': '1080p',  # High quality for spiritual content
                    'quality': 'high',
                    'segments': 4,  # Sanskrit, Translation, Applications, Practice
                    'style': 'cinematic_spiritual_documentary'
                },
                
                'audio': {
                    'voice_style': 'wise_contemplative',
                    'background_music': 'indian_classical_peaceful',
                    'sanskrit_pronunciation': True,
                    'meditation_pace': True  # Slower, more reflective pacing
                },
                
                'visual': {
                    'theme': 'spiritual_cinematic',
                    'color_palette': 'warm_golden_sacred',
                    'imagery': [
                        'lotus_flowers',
                        'ancient_temples',
                        'serene_nature',
                        'modern_life_applications',
                        'meditation_scenes'
                    ],
                    'transitions': 'peaceful_dissolves'
                },
                
                'content': {
                    'sanskrit_display': True,
                    'pronunciation_guide': True,
                    'real_life_examples': True,
                    'contemplation_prompts': True,
                    'daily_practice_guide': True
                }
            })
            
            # Initialize pipeline
            self.pipeline = VideoPipeline(self.config)
            
            logger.info("✅ Bhagavad Gita video pipeline ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup pipeline: {e}")
            return False
    
    def create_contemplative_script(self, verse_key: str) -> str:
        """Create a comprehensive contemplative video script"""
        
        if verse_key not in self.gita_database:
            raise ValueError(f"Verse {verse_key} not found in database")
        
        verse = self.gita_database[verse_key]
        
        script = f"""
[OPENING - Sacred Atmosphere - 0:00-0:20]
Visual: Golden temple at sunrise, lotus flowers floating on peaceful water, soft chanting in background
Text: "Bhagavad Gita - Chapter {verse_key.split('.')[0]}, Verse {verse_key.split('.')[1]}"
Narrator: "Welcome to this contemplative journey with the timeless wisdom of the Bhagavad Gita. Today we explore a verse that can transform how we approach life's challenges."

[SANSKRIT VERSE - 0:20-0:50]
Visual: Ancient Sanskrit text appearing elegantly on golden background, temple bells ringing softly
Text Display: "{verse['sanskrit']}"
Narrator: "Let us first hear this sacred verse in its original Sanskrit:"
Sanskrit Audio: "{verse['pronunciation']}"
Narrator: "Take a moment to feel the vibrational power of these ancient sounds."

[TRANSLATION & MEANING - 0:50-1:30]
Visual: Serene mountain landscape, flowing river, peaceful morning light
Text Display: "{verse['translation']}"
Narrator: "The translation reveals: {verse['translation']}"
Pause for reflection (3 seconds)
Narrator: "This verse teaches us about {verse['theme']}. At its heart, it reminds us that we have the power to choose our response to life's circumstances."

[REAL-LIFE APPLICATION 1 - 1:30-2:20]
Visual: Modern office setting, person facing work challenges, gentle realistic lighting
Narrator: "Let's explore how this wisdom applies to {verse['life_applications'][0]['situation']}."
Text Display: "{verse['life_applications'][0]['situation']}"
Narrator: "{verse['life_applications'][0]['explanation']}"
Pause for contemplation (2 seconds)
Narrator: "For example: {verse['life_applications'][0]['real_example']}"
Text Display: "Practice: {verse['life_applications'][0]['practice']}"

[REAL-LIFE APPLICATION 2 - 2:20-3:10]
Visual: Home setting, family interactions, warm natural lighting
Narrator: "Another powerful application is in {verse['life_applications'][1]['situation']}."
Text Display: "{verse['life_applications'][1]['situation']}"
Narrator: "{verse['life_applications'][1]['explanation']}"
Pause for contemplation (2 seconds)
Narrator: "Consider this scenario: {verse['life_applications'][1]['real_example']}"
Text Display: "Practice: {verse['life_applications'][1]['practice']}"

[REAL-LIFE APPLICATION 3 - 3:10-4:00]
Visual: Various interpersonal situations, coffee shop conversations, peaceful settings
Narrator: "Finally, this wisdom transforms {verse['life_applications'][2]['situation']}."
Text Display: "{verse['life_applications'][2]['situation']}"
Narrator: "{verse['life_applications'][2]['explanation']}"
Pause for contemplation (2 seconds)
Narrator: "Imagine: {verse['life_applications'][2]['real_example']}"
Text Display: "Practice: {verse['life_applications'][2]['practice']}"

[DAILY PRACTICE GUIDE - 4:00-4:40]
Visual: Beautiful garden path, sunrise meditation scene, person in quiet reflection
Narrator: "To integrate this wisdom into your daily life, try these practices:"
Text Display: "Daily Practices"
Narrator: "Morning: {verse['daily_practices'][0]}"
Pause (2 seconds)
Narrator: "Throughout the day: {verse['daily_practices'][1]}"
Pause (2 seconds)  
Narrator: "Evening: {verse['daily_practices'][2]}"

[CONTEMPLATION QUESTIONS - 4:40-5:00]
Visual: Peaceful nature scene, flowing water, soft golden light
Narrator: "As you go forward, contemplate these questions:"
Text Display: "{verse['contemplation_questions'][0]}"
Pause (3 seconds)
Text Display: "{verse['contemplation_questions'][1]}"
Pause (3 seconds)
Text Display: "{verse['contemplation_questions'][2]}"
Narrator: "Let these questions guide your self-reflection and growth."

[CLOSING BLESSING - 5:00-5:20]
Visual: Return to lotus and temple imagery, peaceful sacred atmosphere
Narrator: "May this ancient wisdom illuminate your path and bring peace to your heart. Remember, the Gita's teachings become powerful only when we contemplate them deeply and apply them courageously in our daily lives."
Text Display: "Om Shanti Shanti Shanti"
Fade to soft golden light

[END]
"""
        
        return script.strip()
    
    def generate_gita_video(
        self,
        verse_key: str = "6.5",
        custom_applications: List[Dict] = None,
        output_name: str = None
    ) -> Dict[str, Any]:
        """Generate a Bhagavad Gita contemplative video"""
        
        if not self.pipeline:
            return {'success': False, 'error': 'Pipeline not initialized'}
        
        logger.info(f"🕉️ Generating Bhagavad Gita video for verse {verse_key}")
        
        # Create contemplative script
        script = self.create_contemplative_script(verse_key)
        
        # Generate output filename
        if not output_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f"bhagavad_gita_{verse_key.replace('.', '_')}_{timestamp}.mp4"
        
        # Generate video
        try:
            result = self.pipeline.generate_video(
                script=script,
                output_name=output_name,
                style="contemplative_spiritual"
            )
            
            if result.get('success'):
                # Create accompanying contemplation guide
                self.create_contemplation_guide(verse_key, result['output_path'])
                
                logger.info(f"✅ Bhagavad Gita video generated successfully")
                logger.info(f"📁 Video: {result['output_path']}")
                
                return {
                    'success': True,
                    'output_path': result['output_path'],
                    'verse': verse_key,
                    'theme': self.gita_database[verse_key]['theme'],
                    'contemplation_guide': f"{result['output_path']}_guide.md",
                    'url': result.get('url')
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_contemplation_guide(self, verse_key: str, video_path: str):
        """Create a written contemplation guide to accompany the video"""
        
        verse = self.gita_database[verse_key]
        guide_path = f"{video_path}_guide.md"
        
        guide_content = f"""# Bhagavad Gita Contemplation Guide
## Chapter {verse_key.split('.')[0]}, Verse {verse_key.split('.')[1]}

### 🕉️ Sanskrit Verse
```
{verse['sanskrit']}
```

### 📖 Pronunciation
```
{verse['pronunciation']}
```

### 🌟 Translation
> {verse['translation']}

### 🎯 Core Theme
**{verse['theme']}**

---

## 🌍 Real-Life Applications

"""
        
        for i, application in enumerate(verse['life_applications'], 1):
            guide_content += f"""### {i}. {application['situation']}

**Understanding:** {application['explanation']}

**Real Example:** {application['real_example']}

**Daily Practice:** {application['practice']}

**Contemplation Moment:** When you find yourself in this situation, pause and ask: "How can I apply the wisdom of this verse right now?"

---

"""
        
        guide_content += f"""## 🌅 Daily Spiritual Practices

"""
        
        for i, practice in enumerate(verse['daily_practices'], 1):
            guide_content += f"{i}. **{practice}**\n\n"
        
        guide_content += f"""## 🤔 Deep Contemplation Questions

"""
        
        for i, question in enumerate(verse['contemplation_questions'], 1):
            guide_content += f"{i}. {question}\n\n"
        
        guide_content += f"""## 📝 Personal Reflection Space

Use this space to write your insights and experiences:

### Week 1 - Understanding
*How does this verse speak to my current life situation?*



### Week 2 - Application  
*Where have I successfully applied this teaching?*



### Week 3 - Challenges
*What obstacles do I face in living this wisdom?*



### Week 4 - Integration
*How has this teaching become part of my daily awareness?*



---

## 🎬 About This Video
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Video file: {video_path}
Theme: {verse['theme']}

## 🙏 Reflection Practice
Watch this video during quiet moments when you need spiritual guidance. Let the teachings sink deeply into your consciousness. The goal is not just intellectual understanding, but practical transformation of how you approach life's challenges.

*Om Shanti Shanti Shanti* 🕉️
"""
        
        # Save the guide
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        logger.info(f"📖 Contemplation guide created: {guide_path}")
    
    def create_series_playlist(self, verses: List[str] = None) -> Dict[str, Any]:
        """Create a series of Bhagavad Gita videos for comprehensive study"""
        
        if not verses:
            # Default essential verses for modern life
            verses = ["2.47", "6.5", "2.62", "18.66"]
        
        logger.info(f"🎬 Creating Bhagavad Gita video series: {len(verses)} videos")
        
        results = []
        for verse_key in verses:
            logger.info(f"Generating video for verse {verse_key}")
            result = self.generate_gita_video(verse_key)
            results.append(result)
            
            if result['success']:
                logger.info(f"✅ Completed verse {verse_key}")
            else:
                logger.error(f"❌ Failed verse {verse_key}: {result.get('error')}")
        
        # Create series summary
        successful_videos = [r for r in results if r['success']]
        
        return {
            'success': len(successful_videos) > 0,
            'total_videos': len(verses),
            'successful_videos': len(successful_videos),
            'videos': successful_videos,
            'themes_covered': [v['theme'] for v in successful_videos]
        }


def main():
    """Main function to demonstrate Bhagavad Gita video generation"""
    print("🕉️ Bhagavad Gita Contemplative Video Generator")
    print("=" * 60)
    print("Create videos that make ancient wisdom applicable to modern life")
    print()
    
    # Initialize generator
    generator = BhagavadGitaVideoGenerator()
    
    if not generator.pipeline:
        print("❌ Setup failed. Please check the installation.")
        return
    
    # Show available verses
    print("📖 Available verses:")
    for verse_key, verse_data in generator.gita_database.items():
        print(f"   {verse_key}: {verse_data['theme']}")
    print()
    
    # Generate a single video (default: Chapter 6, Verse 5 - Self-mastery)
    print("🎬 Generating contemplative video for Bhagavad Gita 6.5...")
    result = generator.generate_gita_video("6.5")
    
    if result['success']:
        print("✅ Video generation completed!")
        print(f"📁 Video: {result['output_path']}")
        print(f"📖 Guide: {result['contemplation_guide']}")
        print(f"🎯 Theme: {result['theme']}")
        
        print("\n🌟 How to use this video:")
        print("1. Watch in a quiet, reflective environment")
        print("2. Read the contemplation guide alongside")
        print("3. Apply the teachings in real-life situations")
        print("4. Journal your experiences and insights")
        print("5. Watch again when facing relevant challenges")
        
    else:
        print(f"❌ Video generation failed: {result.get('error')}")
    
    # Option to generate series
    print("\n🎬 Would you like to generate a complete series?")
    print("This will create videos for all 4 essential verses for modern life")


if __name__ == "__main__":
    main()
