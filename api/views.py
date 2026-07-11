from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from .models import Partner, NewsItem, Banner
from .serializers import PartnerSerializer, NewsItemSerializer, BannerSerializer

def check_api_key(request):
    api_key = request.headers.get('X-API-Key')
    expected_key = getattr(settings, 'ADMIN_API_KEY', 'eduvisa_secret_key')
    if not api_key or api_key != expected_key:
        raise PermissionDenied("API Key noto'g'ri yoki taqdim etilmadi.")

class PartnerPublicList(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        qs = Partner.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        return Response(PartnerSerializer(qs, many=True).data)

class PartnerAdminListCreate(APIView):
    def get(self, request):
        check_api_key(request)
        qs = Partner.objects.all()
        return Response(PartnerSerializer(qs, many=True).data)
        
    def post(self, request):
        check_api_key(request)
        ser = PartnerSerializer(data=request.data)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)

class PartnerAdminDetail(APIView):
    def put(self, request, pk):
        check_api_key(request)
        obj = Partner.objects.get(pk=pk)
        ser = PartnerSerializer(obj, data=request.data, partial=True)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response(ser.data)
            
    def delete(self, request, pk):
        check_api_key(request)
        obj = Partner.objects.get(pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NewsPublicList(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        qs = NewsItem.objects.filter(is_published=True)[:limit]
        return Response(NewsItemSerializer(qs, many=True).data)

class NewsPublicDetail(APIView):
    def get(self, request, slug):
        try:
            obj = NewsItem.objects.get(slug=slug, is_published=True)
            return Response(NewsItemSerializer(obj).data)
        except NewsItem.DoesNotExist:
            return Response({"detail": "Topilmadi"}, status=status.HTTP_404_NOT_FOUND)

class NewsAdminListCreate(APIView):
    def get(self, request):
        check_api_key(request)
        qs = NewsItem.objects.all()
        return Response(NewsItemSerializer(qs, many=True).data)
        
    def post(self, request):
        check_api_key(request)
        ser = NewsItemSerializer(data=request.data)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)

class NewsAdminDetail(APIView):
    def put(self, request, pk):
        check_api_key(request)
        obj = NewsItem.objects.get(pk=pk)
        ser = NewsItemSerializer(obj, data=request.data, partial=True)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response(ser.data)
            
    def delete(self, request, pk):
        check_api_key(request)
        obj = NewsItem.objects.get(pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BannerPublicList(APIView):
    def get(self, request):
        qs = Banner.objects.filter(is_active=True)
        return Response(BannerSerializer(qs, many=True).data)

class BannerAdminListCreate(APIView):
    def get(self, request):
        check_api_key(request)
        qs = Banner.objects.all()
        return Response(BannerSerializer(qs, many=True).data)
        
    def post(self, request):
        check_api_key(request)
        ser = BannerSerializer(data=request.data)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)

class BannerAdminDetail(APIView):
    def put(self, request, pk):
        check_api_key(request)
        obj = Banner.objects.get(pk=pk)
        ser = BannerSerializer(obj, data=request.data, partial=True)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response(ser.data)
            
    def delete(self, request, pk):
        check_api_key(request)
        obj = Banner.objects.get(pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)