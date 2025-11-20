"""
CRITICAL FIX: Clean ALL Cloudinary URLs in database
Usage: python manage.py clean_cloudinary_db
"""
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Clean all broken Cloudinary URLs from database'

    def handle(self, *args, **options):
        self.stdout.write("🧹 CLEANING DATABASE...\n")
        
        fixed_count = 0
        
        with transaction.atomic():
            # Clean HeroSlide
            from apps.cms.models import HeroSlide
            for slide in HeroSlide.objects.all():
                if slide.image and slide.image.name:
                    old = slide.image.name
                    
                    # If contains full URL or https - extract only the path
                    if 'https:/' in old or 'http:/' in old or 'res.cloudinary.com' in old:
                        # Extract everything after last /upload/
                        parts = old.split('/upload/')
                        if len(parts) > 1:
                            clean_path = parts[-1]
                            # Remove any remaining https:/
                            clean_path = clean_path.replace('https:/', '').replace('http:/', '').strip('/')
                            
                            slide.image.name = clean_path
                            slide.save()
                            self.stdout.write(f"✅ HeroSlide #{slide.id}")
                            self.stdout.write(f"   Old: {old}")
                            self.stdout.write(f"   New: {clean_path}\n")
                            fixed_count += 1
            
            # Clean ExpertCard
            from apps.cms.models import ExpertCard
            for expert in ExpertCard.objects.all():
                if expert.photo and expert.photo.name:
                    old = expert.photo.name
                    
                    if 'https:/' in old or 'http:/' in old or 'res.cloudinary.com' in old:
                        parts = old.split('/upload/')
                        if len(parts) > 1:
                            clean_path = parts[-1]
                            clean_path = clean_path.replace('https:/', '').replace('http:/', '').strip('/')
                            
                            expert.photo.name = clean_path
                            expert.save()
                            self.stdout.write(f"✅ ExpertCard #{expert.id}: {clean_path}\n")
                            fixed_count += 1
            
            # Clean Course
            from apps.content.models import Course
            for course in Course.objects.all():
                if course.thumbnail and course.thumbnail.name:
                    old = course.thumbnail.name
                    
                    if 'https:/' in old or 'http:/' in old or 'res.cloudinary.com' in old:
                        parts = old.split('/upload/')
                        if len(parts) > 1:
                            clean_path = parts[-1]
                            clean_path = clean_path.replace('https:/', '').replace('http:/', '').strip('/')
                            
                            course.thumbnail.name = clean_path
                            course.save()
                            self.stdout.write(f"✅ Course #{course.id}: {clean_path}\n")
                            fixed_count += 1
                
                if course.logo and course.logo.name:
                    old = course.logo.name
                    
                    if 'https:/' in old or 'http:/' in old or 'res.cloudinary.com' in old:
                        parts = old.split('/upload/')
                        if len(parts) > 1:
                            clean_path = parts[-1]
                            clean_path = clean_path.replace('https:/', '').replace('http:/', '').strip('/')
                            
                            course.logo.name = clean_path
                            course.save()
                            self.stdout.write(f"✅ Course Logo #{course.id}: {clean_path}\n")
                            fixed_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 DONE! Cleaned {fixed_count} images"))
        self.stdout.write("\n🔄 Now DELETE the image in Admin and UPLOAD NEW ONE!")

