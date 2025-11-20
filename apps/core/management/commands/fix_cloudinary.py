"""
Management command to fix all Cloudinary URLs in database
Usage: python manage.py fix_cloudinary
"""
from django.core.management.base import BaseCommand
from django.db import transaction
import cloudinary.api


class Command(BaseCommand):
    help = 'Fix all Cloudinary image URLs in database'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Fixing Cloudinary URLs...\n")
        
        # Get all files from Cloudinary
        self.stdout.write("📥 Getting files from Cloudinary...")
        all_files = {}
        
        try:
            resources = cloudinary.api.resources(type="upload", max_results=500)
            for res in resources['resources']:
                public_id = res['public_id']
                # Store by filename for easier matching
                filename = public_id.split('/')[-1]
                all_files[filename] = public_id
            
            self.stdout.write(f"✅ Found {len(all_files)} files on Cloudinary\n")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error getting Cloudinary files: {e}"))
            return
        
        fixed_count = 0
        
        with transaction.atomic():
            # Fix HeroSlide
            from apps.cms.models import HeroSlide
            for slide in HeroSlide.objects.all():
                if slide.image and slide.image.name:
                    old_name = slide.image.name
                    
                    # Extract filename
                    if '/' in old_name:
                        filename = old_name.split('/')[-1].split('.')[0]
                    else:
                        filename = old_name.split('.')[0]
                    
                    # Find matching file on Cloudinary
                    for key, public_id in all_files.items():
                        if filename in key or filename in public_id:
                            slide.image.name = public_id
                            slide.save()
                            self.stdout.write(f"✅ Fixed HeroSlide #{slide.id}: {public_id}")
                            fixed_count += 1
                            break
            
            # Fix ExpertCard
            from apps.cms.models import ExpertCard
            for expert in ExpertCard.objects.all():
                if expert.photo and expert.photo.name:
                    old_name = expert.photo.name
                    
                    if '/' in old_name:
                        filename = old_name.split('/')[-1].split('.')[0]
                    else:
                        filename = old_name.split('.')[0]
                    
                    for key, public_id in all_files.items():
                        if filename in key or filename in public_id:
                            expert.photo.name = public_id
                            expert.save()
                            self.stdout.write(f"✅ Fixed ExpertCard #{expert.id}: {public_id}")
                            fixed_count += 1
                            break
            
            # Fix Course
            from apps.content.models import Course
            for course in Course.objects.all():
                if course.thumbnail and course.thumbnail.name:
                    old_name = course.thumbnail.name
                    
                    if '/' in old_name:
                        filename = old_name.split('/')[-1].split('.')[0]
                    else:
                        filename = old_name.split('.')[0]
                    
                    for key, public_id in all_files.items():
                        if filename in key or filename in public_id:
                            course.thumbnail.name = public_id
                            course.save()
                            self.stdout.write(f"✅ Fixed Course #{course.id}: {public_id}")
                            fixed_count += 1
                            break
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Done! Fixed {fixed_count} images"))
        self.stdout.write("\n✅ Now check your site - images should work!")

