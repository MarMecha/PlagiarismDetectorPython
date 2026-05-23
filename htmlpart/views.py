from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import *
import difflib 
import re
from django.conf import settings
import os
import time


from .text_extraction import extract_text_with_positions
from .fingerprinting import generate_fingerprints
from .highlighting import *
# Create your views here.

def home(request):
    return render(request, 'home.html')

def signUp(request):
    show_modal = None 
    if request.method == "POST":

        if 'teacher_submit' in request.POST:
            form = TeacherForm(request.POST or None)
            if form.is_valid():
                form.save()
                return redirect('home')
                messages.success(request, "Teacher sign-up successful!")
            else:
                messages.error(request, "There was an Error in your form!")
                show_modal = 'teacher'

        elif 'student_submit' in request.POST:
            form = StudentForm(request.POST or None)
            if form.is_valid():
                form.save()
                messages.success(request, "Student sign-up successful!")
                return redirect('home')
            else:
                messages.error(request, "There was an Error in your form!")
                show_modal = 'student'
        

    return render(request, 'home.html', {'show_modal': show_modal})

def signIn(request):
    show_signIn_modal = False

    if request.method == "POST":
        uni_Mail = request.POST['uni_Mail']
        password = request.POST['password']

        teacher = Teacher.objects.filter(uni_Mail=uni_Mail, password=password).first()
        student = Student.objects.filter(uni_Mail=uni_Mail, password=password).first()
        
        if teacher:

            request.session['teacher_id'] = teacher.id
            request.session['first_name'] = teacher.first_name
            request.session['last_name'] = teacher.last_name

            return redirect('TeacherPage')

        elif student:
            return redirect('StudentPage')

        else: 
            messages.error(request, "Error! Wrong mail or password.")
            show_signIn_modal = True
    
    return render(request, 'home.html', {'show_signIn_modal': show_signIn_modal})

def signOut(request):
    if request.method == 'POST':
        # Clear all session data
        request.session.flush()
        return redirect('home')
    # Handle GET requests safely (optional)
    return redirect('home')



# ----------   Πρόσβασιμότητα   ----------------

def get_teacher_or_redirect(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return None
    try:
        return Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return None


# ----------   Λήψη στοιχείων καθηγητή για UI  ----------------

def get_base_context(teacher):
    return {
        'first_name': teacher.first_name,
        'last_name': teacher.last_name,
        'files': File.objects.filter(teacher=teacher),
        'history_results': Results.objects.filter(teacher=teacher).order_by('-created_at')[:20],
        'show_modal': False
    }

# ---------- Εμφανίζει τα pdf του κάθε καθηγητή με το ανάλογο ID --------------

def validate_file_ids(request):
    file_id1 = request.POST.get('file_id1')
    file_ids_str = request.POST.get('file_ids')
    if not file_id1 or not file_ids_str:
        return None, None
    try:
        file_ids = [int(id) for id in file_ids_str.split(',')]
        return file_id1, file_ids
    except ValueError:
        return None, None

            
# ----------   Αποθήκευση αποτελεσμάτων στο ιστορικό  ----------------

def save_to_history(teacher, file1, file_ids, overall_percentage):
    all_files = File.objects.filter(teacher=teacher)

    # Check if compared to all files
    if len(file_ids) == all_files.count() - 1:
        comparison_files_string = "All"
    else:
        file_names = []
        for fid in file_ids:
            f = all_files.filter(id=fid).first()
            if f:
                file_names.append(os.path.basename(f.file.name))
        if len(file_names) > 2:
            comparison_files_string = ", ".join(file_names[:2]) + "..."
        else:
            comparison_files_string = ", ".join(file_names)

    files_string = ",".join(str(fid) for fid in file_ids)
    
    # Save the result
    Results.objects.create(
        teacher=teacher,
        file1_name=os.path.basename(file1.file.name),
        files_name=comparison_files,
        percentage=overall_percentage   # <--- lowercase
    )


    # Keep only latest 20 history entries
    if Results.objects.filter(teacher=teacher).count() > 20:
        oldest_result = Results.objects.filter(teacher=teacher).order_by('created_at').first()
        if oldest_result:
            oldest_result.delete()



# ----------   workflow για συγκριση, highlight και αποτελεσματα  ----------------

def generate_plagiarism_report(file_id1, file_ids, teacher):
    from .models import Results  # Import here to avoid circular imports
    import os

    file1 = File.objects.filter(id=file_id1, teacher=teacher).first()
    comparison_files = File.objects.filter(id__in=file_ids, teacher=teacher)

    if not file1 or len(comparison_files) != len(file_ids):
        raise Exception("File(s) not found.")

    file1_fps = file1.fingerprints
    file1_hashes = {fp.split("|")[0] for fp in file1_fps}
    total_file1_hashes = len(file1_hashes)

    if total_file1_hashes == 0:
        raise Exception("Primary file has no valid fingerprints.")

    fp_start_map = {}
    k = 7  # shingle size

    for fp in file1_fps:
        try:
            hash_part, start_idx = fp.split("|")
            start_idx = int(start_idx)
            fp_start_map[hash_part] = start_idx
        except (ValueError, AttributeError, IndexError):
            continue

    results = []
    highlight_data = []
    color_mapping = {}
    color_palette = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD",
        "#D4A5A5", "#6A4C93", "#1982C4", "#FF595E", "#8AC926",
        "#FFCA3A", "#34623F", "#5C374D", "#A846A0", "#5995ED",
        "#FAA613", "#6D6875", "#B5838D", "#F72585", "#7209B7",
        "#3A0CA3", "#4361EE", "#4CC9F0", "#F48C06"
    ]
    all_common_hashes = set()

    for idx, cf in enumerate(comparison_files):
        color = color_palette[idx % len(color_palette)]
        color_mapping[cf.id] = color

        cf_hashes = {fp.split("|")[0] for fp in cf.fingerprints}
        common_hashes = file1_hashes & cf_hashes
        all_common_hashes.update(common_hashes)

        file_similarity = len(common_hashes) / total_file1_hashes * 100
        results.append({
            'file_id': cf.id,
            'comparison_file_name': cf.file.name,
            'percentage_taken': file_similarity,
            'color': color
        })

        for fp_hash in common_hashes:
            if fp_hash in fp_start_map:
                start_idx = fp_start_map[fp_hash]
                word_indexes = list(range(start_idx, start_idx + k))
                for idx in word_indexes:
                    try:
                        pos = file1.text_positions[idx]
                        highlight_data.append({
                            'page': pos['page'],
                            'x0': pos['x0'],
                            'y0': pos['y0'],
                            'x1': pos['x1'],
                            'y1': pos['y1'],
                            'color': color,
                            'source_file': cf.id
                        })
                    except IndexError:
                        continue

    highlight_data = merge_highlights(highlight_data)
    overall_percentage = round(len(all_common_hashes) / total_file1_hashes * 100)

    results.sort(key=lambda x: x['percentage_taken'], reverse=True)

    for index, result in enumerate(results, start=1):
        result['position'] = index

    rank_mapping = {result['file_id']: result['position'] for result in results}

    for h in highlight_data:
        source_id = int(h['source_file'])
        h['rank'] = rank_mapping.get(source_id, 'UNKNOWN')

    output_filename = f"highlights_{file1.id}.pdf"
    output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

    create_highlights_pdf(
        original_path=file1.file.path,
        matches=highlight_data,
        output_path=output_path
    )

    # === SAVE TO DATABASE === #
    all_files_count = File.objects.filter(teacher=teacher).count() - 1
    if len(file_ids) == all_files_count:
        comparison_files_string = "All"
    else:
        file_names = []
        for fid in file_ids:
            f = File.objects.filter(id=fid, teacher=teacher).first()
            if f:
                file_names.append(os.path.basename(f.file.name))
        if len(file_names) > 2:
            comparison_files_string = ", ".join(file_names[:2]) + "..."
        else:
            comparison_files_string = ", ".join(file_names)

    # Save to Results
    Results.objects.create(
        teacher=teacher,
        file1_name=os.path.basename(file1.file.name),
        comparison_files=comparison_files_string,
        percentage=overall_percentage
    )

    return {
        'file1_name': file1.file.name,
        'file1_url': file1.file.url,
        'results': results,
        'highlighted_pdf_url': f"{settings.MEDIA_URL}{output_filename}",
        'overall_percentage': overall_percentage,
        'color_mapping': color_mapping
    }

# ----------   workflow για κινήσεις στο UI  ----------------

def teacherPage(request):
    teacher = get_teacher_or_redirect(request)
    if not teacher:
        messages.error(request, "Please log in first.")
        return redirect('signIn')

    context = get_base_context(teacher)

    if request.method == 'POST':
        file_id1, file_ids = validate_file_ids(request)
        if not file_id1 or not file_ids:
            messages.error(request, "Both files must be selected.")
            return render(request, 'TeacherPage.html', context)

        try:
            plagiarism_results = generate_plagiarism_report(file_id1, file_ids, teacher)
            request.session['plagiarism_results'] = plagiarism_results
            return redirect(reverse('TeacherPage') + '#results')
        except Exception as e:
            messages.error(request, f"Processing error: {str(e)}")
            return render(request, 'TeacherPage.html', context)

    if 'plagiarism_results' in request.session:
        context.update(request.session.pop('plagiarism_results'))
        context['show_modal'] = True

    return render(request, 'TeacherPage.html', context)



def delete_files(request):
    if request.method == 'POST':
        try:
            file_ids = request.POST.get('file_ids', '')
            if not file_ids:
                messages.error(request, "No files selected for deletion!")
                return redirect('TeacherPage')

            # Convert string of IDs to list of integers
            file_ids = [int(id) for id in file_ids.split(',') if id.strip().isdigit()]
            
            # Get files and delete them
            files_to_delete = File.objects.filter(id__in=file_ids)
            if not files_to_delete.exists():
                messages.error(request, "No valid files selected for deletion!")
                return redirect('TeacherPage')

            # Delete files and their associated storage
            count = 0
            for file in files_to_delete:
                file.file.delete(save=False)  # Delete the actual file from storage
                file.delete()  # Delete the database record
                count += 1

        except Exception as e:
            messages.error(request, f"Error deleting files: {str(e)}")

        return redirect('TeacherPage')
    
    messages.error(request, "Invalid request method!")
    return redirect('TeacherPage')


def add_files(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        messages.error(request, "Please log in first.")
        return redirect('signIn')

    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher not found.")
        return redirect('signIn')

    if request.method == "POST" and 'file_submit' in request.POST:
        # Get list of uploaded files (could be 1 or many)
        uploaded_list = request.FILES.getlist('files')
        if not uploaded_list:
            messages.error(request, "No files selected!")
            return redirect('TeacherPage')

        successes = 0
        for uploaded in uploaded_list:
            file_name = uploaded.name

            # Skip duplicates for this teacher
            if File.objects.filter(filename=file_name, teacher=teacher).exists():
                continue

            # Save new File instance
            new_file = File(filename=file_name, teacher=teacher)
            new_file.file.save(file_name, uploaded)
            new_file.save()

            try:
                # Extract text & positions
                raw_text, positions = extract_text_with_positions(new_file.file.path)

                # Generate fingerprints
                new_file.fingerprints = generate_fingerprints(raw_text)
                new_file.text_positions = positions
                new_file.save(update_fields=['fingerprints', 'text_positions'])

                successes += 1
            except Exception as e:
                # Clean up if something went wrong
                new_file.file.delete(save=False)
                new_file.delete()
                messages.warning(request, f"Failed to process '{file_name}': {e}")

        return redirect('TeacherPage')

    # If not POST or no file_submit, just render the page
    context = {
        'first_name': teacher.first_name,
        'last_name':  teacher.last_name,
        'files':       File.objects.filter(teacher=teacher),
        'history_results': [],
        'show_modal': False,
    }
    return render(request, 'TeacherPage.html', context)
    
def studentPage(request):
    return render(request, 'StudentPage.html')




