from datetime import date, datetime
from django.db.models import Count
from django.contrib.auth.models import User

import stripe
import twilio
import twilio.rest
import twilio.twiml

from server.models import Labourer, Contractor, Job
from server.serializers import UserSerializer, LabourerSerializer, ContractorSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from push_notifications.models import GCMDevice

stripe.api_key = "sk_test_z1fxtlyji1zu4eZj5KaKQV9Q"

class LabourerList(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        device = GCMDevice.objects.create(registration_id=request.data.get('registration_id')) # create new GCMDevice with the given registration_id
        user = User.objects.get(username = request.data.get('username'))
        requestData = request.data.copy() # Make a mutable copy of the request
        requestData['user'] = user.id # Set the user field to requesting user
        requestData['device'] = device.id 

        serializer = LabourerSerializer(data = requestData)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    def get(self, request, *args, **kwargs):
        labourer = Labourer.objects.get(user=request.user)
        serializer = LabourerSerializer(labourer)
        return Response(serializer.data)

class LabourerDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Modifies the profile of the requesting user
    def put(self, request, format = None): 
        labourer = Labourer.objects.get(user_id = request.user.id) 
        requestData = request.data.copy() # Make a mutable copy of the request
        requestData['user'] = labourer.user_id # Set the user field to requesting user
        #Check if user has a new device id. Update it if there is 
        device_id = request.data.get('device_id')
        if device_id != None:
            device = profile.device 
            device.registration_id = device_id;
            device.save();
         
       #Check if user's email is the same as the one in the database, don't update it if it is
        oldEmail = request.user.email
        if (oldEmail == requestData.get('email') ):
            del requestData['email']

        serializer = UserSerializer(request.user, data = requestData, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        serializer = LabourerSerializer(labourer, data = requestData, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    # Deletes a user and the corresponding user profile
    def delete(self, request, format = None):
        user = User.objects.get(id = request.user.id) # Get the instance of the requesting user and the user profile
        labourer = Labourer.objects.get(user_id = user.id)
        user.delete() # Delete both the user and the corresponding labourer profile
        labourer.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class ContractorList(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        device = GCMDevice.objects.create(registration_id=request.data.get('registration_id')) # create new GCMDevice with the given registration_id
        user = User.objects.get(username = request.data.get('username'))
        requestData = request.data.copy() # Make a mutable copy of the request
        requestData['user'] = user.id # Set the user field to requesting user
        requestData['device'] = device.id 
        
        serializer = ContractorSerializer(data = requestData)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        contractor = Contractor.objects.get(user_id=request.user.id)
        serializer = ContractorSerializer(contractor)
        return Response(serializer.data)

class ContractorDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Modifies the profile of the requesting user
    def put(self, request, format = None): 
        contractor = Contractor.objects.get(user_id = request.user.id)
        requestData = request.data.copy() # Make a mutable copy of the request
        requestData['user'] = contractor.user_id # Set the user field to requesting user
        #Check if user has a new device id. Update it if there is 
        device_id = request.data.get('device_id')
        if device_id != None:
            device = profile.device 
            device.registration_id = device_id;
            device.save();
         
       #Check if user's email is the same as the one in the database, don't update it if it is
        oldEmail = request.user.email
        if (oldEmail == requestData.get('email') ):
            del requestData['email']

        serializer = UserSerializer(request.user, data = requestData, partial = True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        serializer = ContractorSerializer(contractor, data = requestData, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    # Deletes a user and the corresponding user profile
    def delete(self, request, format = None):
        user = User.objects.get(id = request.user.id) # Get the instance of the requesting user and the user profile
        contractor = Contractor.objects.get(user_id = user.id)
        user.delete() # Delete both the user and the corresponding labourer profile
        contractor.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class LabourerSearch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        labourers = Labourer.objects.filter(
                carpentry__gte = request.data.get('carpentry'),
                concrete_forming__gte = request.data.get('concrete_forming'),
                )[:10]

        if len(labourers) > 0:
            account_sid = "AC08df92424485a65eae07469de8b4f54a"
            auth_token  = "54b9efef9832db47965e5568dba86f3b"
            client = twilio.rest.TwilioRestClient(account_sid, auth_token)
            employer = Contractor.objects.get(user = request.user)
            
            job = Job.objects.create(job_code = request.data.get('job_code'), contractor = employer, expired = "false")
            
            for labourer in labourers:
                labourer.device.send_message("You have a new job waiting for you. Check your text messages, and reply ASAP to secure the job")
                job.labourer.add(labourer)
                try:
                    message = client.messages.create(
                            body = "You have a new job pending." + "\nJob code: "
                                + request.data.get('job_code') + "\nStart date (YYYY MM DD): " 
                                + request.data.get('start_date') + "\nStart time (Hour Minute): "
                                + request.data.get('start_time') + "\nAddress of the job: "
                                + request.data.get('job_address') + "\nReply \"Accept\" followed by a space and the \"Job Code\" above to accept the job offer. "
                                + "Example: \"Accept ajhp2015512325\" (without quotes)",
                            to = labourer.phone_number,
                            from_="+16042569605")
                    return Response(request.data, status=status.HTTP_200_OK)
                except twilio.TwilioRestException as e:
                    return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_404_NOT_FOUND)

class PaymentList(APIView): 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        charge_amount = request.data.get('charge_amount')
        token = request.data.get('stripe_token')
        contractor = Contractor.objects.get(user_id = request.user.id)
        # Charge 
        try:
            charge = stripe.Charge.create(
                amount = int(charge_amount), # in cents
                currency = "cad",
                source = token,
                description = "labour charge"
            )
        except stripe.error.CardError, e:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
        
        account_sid = "AC08df92424485a65eae07469de8b4f54a" # Twilio account id
        auth_token  = "54b9efef9832db47965e5568dba86f3b" # Twilio API authentication token
        client = twilio.rest.TwilioRestClient(account_sid, auth_token) # consume the Twilio REST API

        amount = '%.2f'%(int(charge_amount) / 100)
        
        try:
            message = client.messages.create(
                body="Transaction successful! Your credit card has been charged $" + str(amount),
                to=contractor.phone_number,
                #to="+17788893349",
                from_="+16042569605") # Replace with your Twilio number

            return Response(request.data, status=status.HTTP_200_OK)
        except twilio.TwilioRestException as e:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

class Twisponse(APIView):
    def post(self, request, format=None):  
        account_sid = "AC08df92424485a65eae07469de8b4f54a"
        auth_token  = "54b9efef9832db47965e5568dba86f3b"
        client = twilio.rest.TwilioRestClient(account_sid, auth_token)
        body = request.data.get('Body')
        bodyList = body.split(" ")
        print bodyList[1] + "eaiwfjewio;afjewaio;fjaew;oifj" 
        if 'Accept' in body:
            try:
                job = Job.objects.get(job_code = bodyList[1])
            except:
                return Response(request.data, status = status.HTTP_400_BAD_REQUEST)
            
            if job.expired == 'true':
                message = client.messages.create(
                    body = "Sorry. Job " + bodyList[1] + " has expired.",
                    to = request.data.get('From'),
                    from_ = "+16042569605")
                return Response(request.data, status = status.HTTP_201_CREATED) 

            contractor = Contractor.objects.get(id = job.contractor.id)
            contractor.device.send_message("We have successfully found you a worker.")
            
            job.expired = "true"
            job.save()
            # message the labourer
            message = client.messages.create(
                body="Thank you for your confirmation! Your job has been confirmed.",
                to = request.data.get('From'),
                from_ = "+16042569605")
            # message the contractor
            message = client.messages.create(
                body="We have found a worker for the job.",
                to = contractor.phone_number,
                from_ = "+16042569605")
            return Response(request.data, status = status.HTTP_201_CREATED)
