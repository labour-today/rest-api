from datetime import date, datetime
from django.db.models import Count
from django.contrib.auth.models import User

import stripe
import twilio
import twilio.rest
import twilio.twiml

from server.models import Labourer, Contractor, Job
from server.serializers import UserSerializer, LabourerSerializer, ContractorSerializer, JobSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from push_notifications.models import GCMDevice

stripe.api_key = "sk_test_tpqZbhSJnsdSaWQmufF8X2us"

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
        labourer = Labourer.objects.get(user=request.user.id)
        serializer = LabourerSerializer(labourer)
        return Response(serializer.data)

class UserList(APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id = request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class JobList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        worker = Labourer.objects.get(user = request.user.id)
        jobs = Job.objects.filter(labourer = worker, expired = 'false')
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class LabourerDetail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Modifies the profile of the requesting user
    def put(self, request, format = None):
        print request.body
        if request.data.get('worker_id') != None:
            labourer = Labourer.objects.get(id = request.data.get('worker_id'))
            worker_rating = float(labourer.rating[:-1])
            num = int(labourer.rating[-1:])
            worker_rating = "%0.2f" % (worker_rating + float(request.data.get('rating')))
            num = num + 1
            labourer.rating = str(worker_rating) + str(num)
            labourer.save()
            return Response(status = status.HTTP_200_OK)

        labourer = Labourer.objects.get(user_id = request.user.id) 
        requestData = request.data.copy() # Make a mutable copy of the request
        requestData['user'] = labourer.user_id # Set the user field to requesting user
        
        # Check if user has a new registration id. Update it if there is 
        device_id = request.data.get('registration_id')
        if device_id != None:
            device = labourer.device 
            device.registration_id = device_id;
            device.save();
         
       # Check if user's username(email) is the same as the one in the database, don't update it if it is
        oldEmail = request.user.username
        if (oldEmail == requestData.get('username')):
            del requestData['username']

        serializer = UserSerializer(request.user, data = requestData, partial = True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        serializer = LabourerSerializer(labourer, data = requestData, partial = True)
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
        token = request.data.get('stripe_token')
        customer = stripe.Customer.create(source=token, description="customer id " + str(user.id))
        requestData['customer_id'] = customer
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
        device_id = request.data.get('registration_id')
        if device_id != None:
            device = contractor.device 
            device.registration_id = device_id;
            device.save();
         
       #Check if user's email is the same as the one in the database, don't update it if it is
        oldEmail = request.user.username
        if (oldEmail == requestData.get('username') ):
            del requestData['username']

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

def requestDataGet(request, job):
    req = request.data.get(job)
    if req == None:
        return 0
    else:
        return req

class LabourerSearch(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        labourers = Labourer.objects.filter(
                carpentry__gte = requestDataGet(request, 'carpentry'),
                concrete_forming__gte = requestDataGet(request,'concrete_forming'),
                general_labour__gte = requestDataGet(request,'general_labour'),
                dry_walling__gte = requestDataGet(request,'dry_walling'),
                painting__gte = requestDataGet(request,'painting'),
                landscaping__gte = requestDataGet(request,'landscaping'),
                machine_operating__gte = requestDataGet(request,'machine_operating'),
                roofing__gte = requestDataGet(request,'roofing'),
                brick_laying__gte = requestDataGet(request,'brick_laying'),
                electrical__gte = requestDataGet(request,'electrical'),
                plumbing__gte = requestDataGet(request,'plumbing'),
                hat__gte = request.data.get('hat'),
                vest__gte = request.data.get('vest'),
                tool__gte = request.data.get('tool')
        )
        print request.body
        print "labourer"
        for labourer in labourers:
            print labourer

        for labourer in labourers:
            print labourer.available[int(request.data.get('start_day'))]
            print labourer.available[0]
            if labourer.available[int(request.data.get('start_day'))] == 'F' and labourer.available[0] == 'F':
                labourers = labourers.exclude(id = labourer.id)

        #labourers.filter(available[int(request.data.get('start_day'))] = 'T')[:10] # Get only labourers that are available on the day

        if len(labourers) > 0:
            employer = Contractor.objects.get(user = request.user)
            
            job = Job.objects.create(
                    job_code = request.data.get('job_code'),
                    job_type = request.data.get('job_type'),
                    contractor = employer, 
                    expired = "false",
                    job_address = request.data.get('job_address'),
                    job_description = request.data.get('job_description'),
                    start_time = request.data.get('start_time'),
                    start_date = request.data.get('start_date'),
                    city = request.data.get('city'),
                    province = request.data.get('province'),
                    wage = request.data.get('wage')
            )
            
            for labourer in labourers:
                job.labourer.add(labourer)
                labourer.device.send_message("You have a new job pending!")
        else:
            return Response(request.data, status=status.HTTP_404_NOT_FOUND)

class PaymentList(APIView): 
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        charge_amount = float(request.data.get('hours_worked')) * 1900
        contractor = Contractor.objects.get(user_id = request.user.id)
        # Charge 
        try:
            charge = stripe.Charge.create(
                amount = int(charge_amount), # in cents
                currency = "cad",
                customer = contractor.customer_id
            )
        except stripe.error.CardError, e:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
        
        account_sid = "AC08df92424485a65eae07469de8b4f54a" # Twilio account id
        auth_token  = "54b9efef9832db47965e5568dba86f3b" # Twilio API authentication token
        client = twilio.rest.TwilioRestClient(account_sid, auth_token) # consume the Twilio REST API

        amount = '%.2f'%(float(charge_amount) / 100)
        
        try:
            message = client.messages.create(
                body="Transaction successful! Your credit card has been charged $" + str(amount),
                to=contractor.phone_number,
                from_="+16042569605") # Replace with your Twilio number

            return Response(request.data, status=status.HTTP_200_OK)
        except twilio.TwilioRestException as e:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

class LabourerResponse(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        if request.data.get('option') == 'accept':
            try:
                job = Job.objects.get(job_code = request.data.get('job_code'))
            except:
                return Response(request.data, status = status.HTTP_400_BAD_REQUEST)

            if job.expired == 'true':
                labourer = Labourer.objects.get(user = request.user.id)
                labourer.device.send_message("Sorry this position has already been filled")
                return Response(request.data, status = status.HTTP_400_BAD_REQUEST)
            
            contractor = Contractor.objects.get(id = job.contractor.id)
            job.expired = "true"
            job.save()

            contractor.device.send_message(
                    "We have found a worker." + 
                    "\nWorker ID: " + str(labourer.id) +
                    "\nWorker name: " + labourer.user.first_name + " " + labourer.user.last_name +
                    "\nWorker phone number: " + str(labourer.phone_number) +
                    "\nPlease keep this information on record for reference."
                    )
            return Response(request.data, status = status.HTTP_201_CREATED)




class Twisponse(APIView):
    def post(self, request, format=None):  
        account_sid = "AC08df92424485a65eae07469de8b4f54a"
        auth_token  = "54b9efef9832db47965e5568dba86f3b"
        client = twilio.rest.TwilioRestClient(account_sid, auth_token)
        body = request.data.get('Body')
        bodyList = body.split(" ")
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
            labourer = Labourer.objects.get(phone_number = request.data.get('From'))

            contractor.device.send_message(
                    "We have successfully found you a worker. Additional info will be sent to you via SMS." 
            )
            job.expired = "true"
            job.save()
            # message the labourer
            message = client.messages.create(
                body="Thank you for your confirmation! Your job has been confirmed.",
                to = request.data.get('From'),
                from_ = "+16042569605")
            # message the contractor
            message = client.messages.create(
                body="We have found a worker for the job." + 
                "\nWorker ID: " + str(labourer.id) +
                "\nWorker name: " + labourer.user.first_name + " " + labourer.user.last_name +
                "\nWorker phone number: " + str(labourer.phone_number) + 
                "\nPlease keep this information on record for reference."
                ,
                to = contractor.phone_number,
                from_ = "+16042569605"
            )
            return Response(request.data, status = status.HTTP_201_CREATED)
