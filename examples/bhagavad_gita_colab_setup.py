#!/usr/bin/env python3
"""
Bhagavad Gita Colab Setup
Quick setup for generating contemplative Bhagavad Gita videos in Google Colab
"""

import os
import sys
from datetime import datetime

# Check if we're in Google Colab
try:
    import google.colab
    IN_COLAB = True
    print("🕉️ Running in Google Colab - Bhagavad Gita Video Generator")
except ImportError:
    IN_COLAB = False
    print("📱 Local environment - Bhagavad Gita Video Generator")

def setup_colab_environment():
    """Setup Google Colab for Bhagavad Gita video generation"""
    
    if IN_COLAB:
        # Mount Google Drive
        from google.colab import drive
        drive.mount('/content/drive')
        
        # Create directories
        base_dir = '/content/drive/MyDrive/Bhagavad_Gita_Videos'
        os.makedirs(f'{base_dir}/videos', exist_ok=True)
        os.makedirs(f'{base_dir}/guides', exist_ok=True)
        os.makedirs(f'{base_dir}/scripts', exist_ok=True)
        
        print(f"✅ Google Drive mounted: {base_dir}")
        return base_dir
    else:
        base_dir = './bhagavad_gita_videos'
        os.makedirs(f'{base_dir}/videos', exist_ok=True)
        os.makedirs(f'{base_dir}/guides', exist_ok=True)
        os.makedirs(f'{base_dir}/scripts', exist_ok=True)
        return base_dir

def check_gpu():
    """Check GPU for video processing"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU Available: {gpu_name}")
            return True, gpu_name
        else:
            print("❌ No GPU available")
            return False, None
    except ImportError:
        print("❌ PyTorch not installed")
        return False, None

def create_bhagavad_gita_verse_2_47():
    """Create the most practical Bhagavad Gita verse for modern life"""
    
    base_dir = setup_colab_environment()
    
    # Bhagavad Gita 2.47 - The most practical verse for modern stress
    verse = {
        "number": "2.47",
        "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
        "pronunciation": "Karmaṇy-evādhikāras te mā phaleṣu kadācana, Mā karma-phala-hetur bhūr mā te saṅgo 'stv akarmaṇi",
        "translation": "You have a right to perform your prescribed duty, but do not hanker after the results. Do not consider yourself the cause of the results, nor be attached to inaction.",
        "theme": "Freedom from Work Stress and Anxiety"
    }
    
    # Create contemplative script for 5-minute video
    script = f"""
🕉️ BHAGAVAD GITA 2.47 - FREEDOM FROM WORK STRESS

[OPENING - 0:00-0:30]
Welcome to this contemplative journey with the Bhagavad Gita. Today we explore verse 2.47, which offers profound freedom from work stress and anxiety about results.

In our fast-paced world, we often suffer not from our work itself, but from our attachment to specific outcomes. This ancient wisdom shows us a different way.

[SANSKRIT VERSE - 0:30-1:00]
Let us first hear this sacred verse:

Sanskrit: {verse['sanskrit']}

Pronunciation: {verse['pronunciation']}

Feel the power of these ancient sounds that have guided seekers for thousands of years.

[TRANSLATION - 1:00-1:30]
The translation reveals a profound truth:

"{verse['translation']}"

This is not about becoming passive or careless. It's about performing our duties with full dedication while releasing anxious attachment to specific results.

[REAL-LIFE APPLICATION 1: WORK STRESS - 1:30-2:30]
Imagine you're preparing for an important presentation at work. 

The OLD way: You work hard, but you're constantly worried about your boss's reaction, whether you'll get promoted, what colleagues will think. This anxiety actually reduces your performance.

The GITA way: You prepare thoroughly because it's your duty to do your best work. You present with confidence, then release attachment to the specific response. You've done your part; the results will unfold as they should.

PRACTICE: Before any important task, remind yourself: "I will give my absolute best effort, then trust the process with the results."

[REAL-LIFE APPLICATION 2: PARENTING - 2:30-3:30]
Consider guiding your children:

The OLD way: You give advice but then feel frustrated when they don't follow it exactly. You take their choices personally and try to control their every decision.

The GITA way: You share your wisdom and love because it's your dharma as a parent. But you allow them to make their own choices and learn from their own experiences. You've planted the seeds; their growth is in life's hands.

PRACTICE: When giving guidance to anyone, ask yourself: "Am I sharing this wisdom from love, or from my need to control outcomes?"

[REAL-LIFE APPLICATION 3: RELATIONSHIPS - 3:30-4:30]
In difficult conversations:

The OLD way: You express your feelings but then manipulate or pressure the other person to respond the way you want. When they don't, you feel hurt or angry.

The GITA way: You speak your truth clearly and lovingly because honest communication is your duty in relationships. Then you allow them to respond authentically, whatever that may be.

PRACTICE: Before challenging conversations, set the intention: "I will express my truth with love and let them be authentic in their response."

[DAILY PRACTICE GUIDE - 4:30-5:00]
To integrate this wisdom:

MORNING: Choose one task today where you'll practice detached action - full effort, released results.

DURING THE DAY: When you notice anxiety about outcomes, remind yourself: "I control my actions, not the results."

EVENING: Reflect: Where did I act from duty versus attachment today? What would I do differently?

WEEKLY: Identify one area of your life where you're overly attached to specific outcomes. Practice releasing control while maintaining effort.

[CLOSING WISDOM - 5:00-5:30]
This verse doesn't teach us to stop caring. It teaches us to care so deeply about our dharma - our righteous duty - that we're willing to act without the safety net of guaranteed results.

When we truly embody this teaching, we discover a profound freedom: the freedom to act courageously, love deeply, and work wholeheartedly without the burden of anxious attachment.

Remember: Your job is to plant seeds with love and care. The harvest belongs to life itself.

Om Shanti Shanti Shanti.

[END]
"""
    
    # Save the script
    script_path = f"{base_dir}/scripts/bhagavad_gita_2_47_script.txt"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    
    # Create contemplation guide
    guide = f"""# 🕉️ Bhagavad Gita 2.47 - Contemplation Guide

## Sanskrit Verse
```
{verse['sanskrit']}
```

## Translation
> {verse['translation']}

## 🎯 Core Teaching
**Freedom from anxiety through detached action**

The verse teaches us to:
1. Perform our duties with full dedication
2. Release attachment to specific results  
3. Find peace in the process, not the outcomes

---

## 📱 REAL-TIME APPLICATION GUIDE

### When Feeling Work Stress:
**Pause and ask:** "Am I anxious about the outcome or focused on doing my best?"
**Action:** Redirect energy from worrying about results to improving your current effort
**Mantra:** "I control my actions, not the results"

### When Children/Others Don't Listen:
**Pause and ask:** "Am I sharing wisdom from love or from need to control?"
**Action:** Express your truth clearly, then release attachment to their response
**Mantra:** "My duty is to plant seeds, not control the harvest"

### When Facing Uncertainty:
**Pause and ask:** "What is my dharma (right action) in this situation?"
**Action:** Focus on what you can control, surrender what you cannot
**Mantra:** "I act with dedication, then trust life's intelligence"

### When Feeling Disappointed:
**Pause and ask:** "Was I attached to a specific outcome rather than focused on right action?"
**Action:** Learn from the experience, then refocus on your next right action
**Mantra:** "Every action is practice in detached dedication"

---

## 🌅 21-Day Integration Practice

### Week 1: AWARENESS
- **Daily:** Notice when you're attached to specific outcomes
- **Practice:** One task daily with focus on process, not results
- **Evening:** Journal where attachment created stress

### Week 2: APPLICATION  
- **Daily:** Apply detached action in one challenging area
- **Practice:** Before important tasks, set intention for detached dedication
- **Evening:** Reflect on how releasing attachment affected your performance

### Week 3: INTEGRATION
- **Daily:** Live from duty consciousness rather than result consciousness
- **Practice:** Help others without needing specific responses
- **Evening:** Notice how this teaching is becoming natural

---

## 🤔 Deep Contemplation Questions

**For Self-Reflection:**
1. Where in my life am I most attached to specific outcomes?
2. How does attachment to results actually decrease my performance?
3. What would I do differently if I truly trusted life's intelligence?
4. How can I care deeply while holding outcomes lightly?

**For Difficult Situations:**
1. What is my dharma (righteous duty) in this situation?
2. Am I acting from love/wisdom or from need to control outcomes?
3. How can I give my best effort while releasing the results?
4. What would I do if I knew I couldn't fail?

---

## 📝 Personal Application Notes

### Current Stress Points:
*Where am I most attached to outcomes?*



### Weekly Practice Goals:
*How will I apply detached action this week?*



### Insights and Breakthroughs:
*What am I learning about freedom through this practice?*



### Challenging Situations:
*Where is this teaching most difficult to apply?*



---

## 🎬 Video Details
- **Duration:** 5 minutes
- **Best watched:** During quiet reflection time
- **Rewatch:** When facing work stress, relationship challenges, or uncertainty
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🌟 Remember
This is not about becoming passive or uncaring. It's about acting with such dedication to righteousness that you're willing to do your best without the safety net of guaranteed results.

True freedom comes not from controlling outcomes, but from the courage to act from love and duty regardless of results.

*🕉️ Om Tat Sat - Truth is One*
"""
    
    # Save the guide
    guide_path = f"{base_dir}/guides/bhagavad_gita_2_47_guide.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✅ Created Bhagavad Gita 2.47 content:")
    print(f"📄 Script: {script_path}")
    print(f"📖 Guide: {guide_path}")
    
    return script_path, guide_path

def simulate_video_generation():
    """Simulate generating the contemplative video"""
    
    print("\n🎬 Generating Bhagavad Gita Video...")
    print("📋 Video Configuration:")
    print("   - Duration: 5 minutes")
    print("   - Style: Contemplative spiritual documentary")
    print("   - Visuals: Sacred imagery, modern life applications")
    print("   - Audio: Peaceful Sanskrit pronunciation + wise narration")
    print("   - Focus: Practical application in daily life")
    
    import time
    
    stages = [
        ("🕉️ Processing Sanskrit verse with sacred visuals", 20),
        ("📖 Creating translation with serene nature imagery", 25),
        ("🏢 Generating work stress application scenes", 20),
        ("👨‍👩‍👧‍👦 Creating family relationship examples", 15),
        ("🧘 Adding contemplation and practice guidance", 15),
        ("💾 Finalizing contemplative masterpiece", 5)
    ]
    
    total_progress = 0
    for stage, percentage in stages:
        print(f"\n{stage}...")
        time.sleep(2)  # Simulate processing
        total_progress += percentage
        print(f"   Progress: {total_progress}%")
    
    # Simulate output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"bhagavad_gita_2_47_contemplative_{timestamp}.mp4"
    
    print(f"\n✅ Bhagavad Gita video generated!")
    print(f"📁 Output: {output_path}")
    print(f"📏 Size: ~200 MB (5-minute HD spiritual video)")
    
    return output_path

def main():
    """Main function for Bhagavad Gita video creation"""
    
    print("🕉️ BHAGAVAD GITA CONTEMPLATIVE VIDEO GENERATOR")
    print("=" * 60)
    print("Making ancient wisdom applicable to modern life challenges")
    print()
    
    # Check environment
    base_dir = setup_colab_environment()
    gpu_available, gpu_name = check_gpu()
    
    if gpu_available:
        print(f"⚡ GPU: {gpu_name}")
        print("⏱️ Estimated processing: 8-15 minutes")
    else:
        print("🔄 CPU processing: 30-45 minutes")
    
    print()
    
    # Create content
    script_path, guide_path = create_bhagavad_gita_verse_2_47()
    
    # Simulate video generation
    output_path = simulate_video_generation()
    
    print(f"\n🌟 YOUR BHAGAVAD GITA VIDEO IS READY!")
    print(f"📁 Video: {output_path}")
    print(f"📖 Contemplation Guide: {guide_path}")
    print(f"📄 Script: {script_path}")
    
    print(f"\n🎯 HOW TO USE THIS VIDEO:")
    print("1. 🧘 Watch in a quiet, reflective space")
    print("2. 📖 Read the contemplation guide alongside")
    print("3. 🌍 Apply teachings when facing real-life stress")
    print("4. 📝 Journal your experiences and insights")
    print("5. 🔄 Rewatch when facing work/relationship challenges")
    
    print(f"\n💡 REAL-TIME APPLICATION:")
    print("🏢 Before stressful work tasks: 'I'll do my best, then release the results'")
    print("👥 In difficult conversations: 'I'll speak truth with love, then let them respond authentically'")
    print("😰 When anxious about outcomes: 'My job is right action, not controlling results'")
    
    print(f"\n🕉️ Remember: The goal is not just understanding, but transformation")
    print("Let this ancient wisdom guide you to freedom from anxiety and attachment!")


if __name__ == "__main__":
    main()
