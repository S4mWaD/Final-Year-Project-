from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Vendor, Questionnaire
from .serializers import VendorSerializer, QuestionnaireSerializer
from .utils import calculate_risk_score, classify_risk
from django.shortcuts import get_object_or_404

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

class VendorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)

class VendorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vendor_id):
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        serializer = VendorSerializer(vendor)
        return Response(serializer.data)

class RiskAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vendor_id):
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        risk_score = calculate_risk_score(vendor)
        risk_category = classify_risk(risk_score)
        return Response({
            'vendor_name': vendor.name,
            'risk_score': risk_score,
            'risk_category': risk_category
        })

class QuestionnaireListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questionnaires = Questionnaire.objects.all()
        serializer = QuestionnaireSerializer(questionnaires, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuestionnaireSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
