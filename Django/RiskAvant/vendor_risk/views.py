from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Vendor, Questionnaire
from .utils import calculate_risk_score, classify_risk

def home(request):
    return render(request, "home.html")

def vendor_questionnaire(request, vendor_id):

    vendor = get_object_or_404(Vendor, pk=vendor_id)
    questions = vendor.get_questions()
    
    return render(request, 'vendor_questionnaire.html', {'vendor': vendor, 'questions': questions})

def submit_questionnaire(request, vendor_id):
    if request.method == "POST":
        vendor = get_object_or_404(Vendor, id=vendor_id)
        responses = []
        
        # Iterate through all questions and save responses
        for question in Questionnaire.objects.filter(vendor_type=vendor.vendor_type):
            answer = request.POST.get(f"answer_{question.id}")
            if answer:
                responses.append((question, answer))  # Save or process each response here
        
                # Response.objects.create(vendor=vendor, question=question, answer=answer)
        
        # Redirect to a success page or back to the vendor detail page
        return redirect('vendor_detail', vendor_id=vendor.id)

    return redirect('vendor_detail', vendor_id=vendor_id)

def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    return render(request, 'vendor_detail.html', {'vendor': vendor})

def get_risk_assessment(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    risk_score = calculate_risk_score(vendor)
    risk_category = classify_risk(risk_score)
    
    return JsonResponse(
        {
            'vendor_name': vendor.name,
            'risk_score': risk_score,
            'risk_category': risk_category
         }
         )