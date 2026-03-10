#!/usr/bin/env python3
"""
Demo script to show email digest functionality with sample data.
This demonstrates what you'll receive via email when the system finds exam-relevant news.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sample_digest():
    """Create a sample exam intelligence digest."""
    return """
# 🎓 Daily Competitive Exam Intelligence Digest for UPSC

**Generated on:** {date}
**Exam Focus:** UPSC Civil Services
**Articles Analyzed:** 15 | **Top Articles Selected:** 5

---

## 📊 Today's Intelligence Summary

**Key Categories:** Economy (2), Polity (2), International Relations (1)
**High Priority Articles:** 3
**Prelims Relevant:** 5
**Mains Relevant:** 4

---

## 🔥 Top Articles for Your Exam Preparation

### 1. RBI Monetary Policy Committee Meeting - Key Decisions (Score: 9.2/10)

**Source:** PIB Press Release | **Category:** Economy | **Published:** 2 hours ago

**Summary:**
The Reserve Bank of India's Monetary Policy Committee concluded its meeting with significant decisions on repo rates and inflation targets. The committee maintained the repo rate at 6.5% while revising growth projections for FY 2024-25.

**Why Important for UPSC:**
- **Prelims Relevance:** Direct questions on current repo rate, MPC composition
- **Mains Relevance:** Economic policy analysis, inflation control mechanisms
- **Essay Potential:** Monetary policy's role in economic stability

**Possible Questions:**
1. What is the current repo rate set by RBI?
2. Analyze the impact of monetary policy on inflation control
3. Discuss the role of MPC in India's economic framework

**Key Facts to Remember:**
- MPC has 6 members (3 RBI + 3 Government nominees)
- Meets 6 times a year
- Current repo rate: 6.5%

---

### 2. India-Australia Strategic Partnership: New Defense Agreements (Score: 8.8/10)

**Source:** YouTube - MEA Official Channel | **Category:** International Relations | **Published:** 4 hours ago

**Summary:**
India and Australia signed comprehensive defense cooperation agreements during the bilateral summit, focusing on maritime security, cyber defense, and joint military exercises in the Indo-Pacific region.

**Why Important for UPSC:**
- **Prelims Relevance:** Recent bilateral agreements, QUAD partnership
- **Mains Relevance:** India's foreign policy, Indo-Pacific strategy
- **Essay Potential:** Strategic partnerships in changing global order

**Possible Questions:**
1. Discuss India-Australia strategic partnership in Indo-Pacific context
2. Analyze the significance of QUAD in regional security
3. Evaluate India's Act East Policy with reference to Australia

**Key Facts to Remember:**
- QUAD members: India, USA, Japan, Australia
- Malabar naval exercises include all QUAD nations
- Australia rejoined QUAD in 2017

---

### 3. Digital India Initiative: New Cybersecurity Framework (Score: 8.5/10)

**Source:** Government Schemes Portal | **Category:** Science & Technology | **Published:** 6 hours ago

**Summary:**
The government launched a comprehensive cybersecurity framework under Digital India, establishing new protocols for data protection, critical infrastructure security, and cyber threat response mechanisms.

**Why Important for UPSC:**
- **Prelims Relevance:** Digital India components, cybersecurity measures
- **Mains Relevance:** Technology governance, data protection policies
- **Essay Potential:** Digital transformation and security challenges

**Possible Questions:**
1. Evaluate the cybersecurity challenges in Digital India implementation
2. Discuss the role of technology in governance transformation
3. Analyze data protection frameworks in India

**Key Facts to Remember:**
- Digital India launched in 2015
- Three pillars: Infrastructure, Services, Empowerment
- CERT-In is national cybersecurity agency

---

### 4. Supreme Court Verdict on Electoral Bonds (Score: 8.3/10)

**Source:** PIB Press Release | **Category:** Polity & Governance | **Published:** 8 hours ago

**Summary:**
The Supreme Court delivered a landmark judgment on electoral bonds, declaring the scheme unconstitutional and ordering disclosure of all bond purchasers and recipients, significantly impacting political funding transparency.

**Why Important for UPSC:**
- **Prelims Relevance:** Electoral reforms, Supreme Court powers
- **Mains Relevance:** Political funding, transparency in democracy
- **Essay Potential:** Electoral reforms and democratic governance

**Possible Questions:**
1. Critically analyze the electoral bond scheme and its implications
2. Discuss the role of judiciary in electoral reforms
3. Evaluate measures for transparency in political funding

**Key Facts to Remember:**
- Electoral bonds introduced in 2018
- Anonymous political funding mechanism
- SC declared it unconstitutional in 2024

---

### 5. Climate Change: India's Updated NDC Targets (Score: 8.0/10)

**Source:** YouTube - PIB India Channel | **Category:** Environment & Ecology | **Published:** 10 hours ago

**Summary:**
India submitted updated Nationally Determined Contributions (NDC) to UNFCCC, committing to achieve net-zero emissions by 2070 and increase renewable energy capacity to 500 GW by 2030.

**Why Important for UPSC:**
- **Prelims Relevance:** Climate agreements, renewable energy targets
- **Mains Relevance:** Environmental policy, sustainable development
- **Essay Potential:** Climate action and development balance

**Possible Questions:**
1. Analyze India's climate commitments under Paris Agreement
2. Discuss challenges in achieving net-zero emissions by 2070
3. Evaluate renewable energy potential in India

**Key Facts to Remember:**
- Paris Agreement signed in 2015
- India's net-zero target: 2070
- Current renewable capacity: ~180 GW

---

## 📈 Weekly Trends Analysis

**Rising Topics:**
- Economic policy reforms
- India-Pacific strategic partnerships
- Digital governance initiatives

**Exam Alert:**
- Increased focus on monetary policy in recent current affairs
- Multiple international agreements this week - track for IR questions
- Technology and governance intersection trending

---

## 🎯 Tomorrow's Focus Areas

Based on current trends, tomorrow's preparation should emphasize:
1. **Economic Survey highlights** - Budget session approaching
2. **QUAD summit outcomes** - Follow-up developments
3. **Digital governance policies** - Implementation challenges

---

## 📚 Recommended Reading

- RBI Annual Report 2023-24 (Chapter on Monetary Policy)
- MEA Statement on India-Australia Strategic Partnership
- Digital India Progress Report 2024

---

**Next Digest:** Tomorrow at 8:00 AM
**Feedback:** Reply to this email with your exam focus areas

*Generated by AI-Powered Competitive Exam News Intelligence System*
*Personalized for UPSC Civil Services Preparation*
""".format(date=datetime.now().strftime("%B %d, %Y at %I:%M %p"))

def send_demo_email():
    """Send a demo digest email."""
    try:
        # Email configuration
        smtp_server = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        username = os.getenv('SMTP_USERNAME')
        password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('EMAIL_FROM', f'Exam Intelligence <{username}>')
        to_email = os.getenv('EMAIL_TO', username)

        if not all([username, password, to_email]):
            print("❌ Email configuration incomplete. Please check your .env file.")
            return False

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎓 Daily UPSC Intelligence Digest - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = from_email
        msg['To'] = to_email

        # Create digest content
        digest_content = create_sample_digest()
        
        # Add text version
        text_part = MIMEText(digest_content, 'plain', 'utf-8')
        msg.attach(text_part)

        # Send email
        print("📧 Sending your daily exam intelligence digest...")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent successfully to {to_email}")
        print(f"📬 Check your inbox for: '{msg['Subject']}'")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

def main():
    """Main function to demonstrate email functionality."""
    print("🎯 COMPETITIVE EXAM INTELLIGENCE SYSTEM - EMAIL DEMO")
    print("=" * 60)
    print()
    print("This demo shows you exactly what you'll receive via email")
    print("when the system finds exam-relevant news articles.")
    print()
    print("📧 Email Configuration:")
    print(f"  From: {os.getenv('EMAIL_FROM', 'Not configured')}")
    print(f"  To: {os.getenv('EMAIL_TO', 'Not configured')}")
    print()
    
    # Show sample digest content
    print("📋 Sample Digest Content (what you'll receive):")
    print("-" * 50)
    sample_digest = create_sample_digest()
    # Show first few lines
    lines = sample_digest.split('\n')[:20]
    for line in lines:
        print(line)
    print("... (full digest continues with detailed analysis)")
    print("-" * 50)
    print()
    
    # Ask user if they want to send demo email
    response = input("📤 Would you like to send this demo digest to your email? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        success = send_demo_email()
        if success:
            print()
            print("🎉 Demo email sent! Here's what happens when you run the real system:")
            print()
            print("📅 DAILY USAGE:")
            print("  python scripts/run_pipeline.py 24 10 --exam-type UPSC")
            print("  → Scrapes latest news from YouTube, PIB, Government portals")
            print("  → AI analyzes and ranks content for UPSC relevance")
            print("  → Sends formatted digest to your email")
            print()
            print("🔄 AUTOMATED SETUP (Optional):")
            print("  Set up a daily cron job or Windows Task Scheduler to run automatically")
            print("  Example: Run every morning at 8 AM for daily exam updates")
            print()
            print("📧 EMAIL CONTENT:")
            print("  ✅ Top 5-10 most relevant articles for your exam")
            print("  ✅ AI-generated summaries with exam focus")
            print("  ✅ Prelims/Mains relevance analysis")
            print("  ✅ Possible exam questions")
            print("  ✅ Key facts to remember")
            print("  ✅ Weekly trends and tomorrow's focus areas")
    else:
        print("📋 No email sent. You can run this demo anytime with:")
        print("  python demo_email_digest.py")

if __name__ == "__main__":
    main()