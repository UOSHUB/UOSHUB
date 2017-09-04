from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.serializers import Serializer, CharField
from requests.exceptions import ConnectionError as NoConnectionError
from . import myudc as udc, blackboard as bb, reports as rep, outlook as ms


# API root (/api/) requests handler
class APIRoot(APIView):
    """
    UOSHUB Restful API root URL.
    Notice that all API calls require login first except for calendar calls.
    """
    # Returns list of available API calls on GET request
    def get(self, request):
        # Provide full API URL to current server
        url = request.build_absolute_uri
        # Display a list of available API calls
        return Response({
            "Login": url("login/"),
            "Layout Details": url("details/"),
            "Updates": url("updates/"),
            "Schedule": url("schedule/"),
            "Emails": url("emails/"),
        })


# Login requests handler
class Login(APIView):
    """
    Login to UOSHUB
    {Sid: Student Id, Pin: Password}
    """
    # Describes login credentials fields
    class Credentials(Serializer):
        sid = CharField()
        pin = CharField()
    # Register fields description in login API
    serializer_class = Credentials

    # Receives credentials data and preforms login on POST request
    def post(self, request):
        # Store submitted credentials
        sid = request.data.get("sid")
        pin = request.data.get("pin")
        # Try logging in and storing Blackboard cookies
        try: bb_cookies = bb.login(sid, pin)
        # If login to Blackboard fails
        except ConnectionError as error:
            # Return error message with BAD_REQUEST status
            return Response(error.args[0], status=400)
        # If Blackboard is down
        except NoConnectionError:
            # Login to outlook, if credentials are wrong
            if not ms.login(sid, pin):
                # Return error message with BAD_REQUEST status
                return Response("Wrong Credentials!", status=400)
        # Otherwise, if logging in to Blackboard succeeds
        else:
            # Store blackboard cookies in session
            request.session["blackboard"] = bb_cookies
        # Store submitted credentials in session
        request.session["student"] = {"sid": sid, "pin": pin}
        # If API is being requested from a browser
        if isinstance(request.accepted_renderer, BrowsableAPIRenderer):
            # Display Django session id in viewer's browser
            return Response({
                "sessionId": request.session.session_key or "Refresh to see it"
            })
        # Otherwise, return an empty response indicating success
        return Response()


# Website's layout details requests handler
class LayoutDetails(APIView):
    """
    This only returns student's basic info right now,
    but in the future it will have all layout details including:
    theme preferences, student's modifications and other settings
    """
    # Returns layout details on GET request
    def get(self, request):
        # Return student's basic info as of now
        return Response({
            # Get student's basic info from Blackboard
            "student": bb.api.basic_info(
                # Send Blackboard cookies
                request.session["blackboard"],
                # And current student id
                request.session["student"]["sid"]
            )
        })


# Student's updates requests handler
class Updates(APIView):
    """
    This returns student's Blackboard updates,
    which is a dictionary of updates and the
    names of the courses they are coming from.
    """
    # Returns updates dictionary of all courses on GET request
    def get(self, request):
        # Return updates object
        return Response(
            # Get & scrape student's updates from Blackboard
            bb.scrape.updates(
                bb.get.updates(
                    # Send Blackboard cookies
                    request.session["blackboard"]
                )
            )
        )


# Student's schedule requests handler
class Schedule(APIView):
    """
    This returns student's schedule details,
    which's a dictionary of courses that contain:
    course id, title, days, time, crn, location, etc..
    """
    # Returns schedule dictionary of requested term on GET request
    def get(self, request, term=None):
        # Return student's schedule details
        return Response(
            # Get & scrape student's basic info from Blackboard
            rep.scrape.schedule_details(
                rep.get.schedule(
                    # Send current student id
                    request.session["student"]["sid"],
                    # And the specified or current term code
                    term  # or bb.get.current_term()
                )
            )
        )


# Student's emails requests handler
class Emails(APIView):
    """
    Emails API root URL
    """
    # Returns list of email related API calls on GET request
    def get(self, request):
        # If URL isn't ending with trailing slash
        if not request.path.endswith("/"):
            # Redirect to one with trailing slash
            return redirect("emails/")
        # Provide emails API URL
        url = request.build_absolute_uri
        # Display a list of available email related API calls
        return Response({
        })
