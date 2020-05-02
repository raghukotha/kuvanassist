# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import datetime
import pytz
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model.services import ServiceException
from ask_sdk_model.services.reminder_management import Trigger, TriggerType, AlertInfo, SpokenInfo, SpokenText, \
    PushNotification, PushNotificationStatus, ReminderRequest, Recurrence
from ask_sdk_model import Response
from ask_sdk_model import Response
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient



import prompts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REQUIRED_PERMISSIONS = ["alexa::alerts:reminders:skill:readwrite"]
TIME_ZONE_ID = 'America/Chicago'

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        logger.info('In LaunchRequestHandler Can Handle')

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = prompts.KUVAN_WELCOME_MESSAGE
        logger.info('In LaunchRequestHandler {speak_output}')

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(SimpleCard('Kuvan Welcoome', speak_output))
                .ask(speak_output)
                .response
        )


class IAmTakingKuvanIntentHandler(AbstractRequestHandler):
    """Handler for IAmTakingKuvan messge."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("IAmTakingKuvanIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        userMedication = slots['userMedication'].value

        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['userMedication'] = userMedication
        
        speak_output = f'You have added Medication {userMedication}. {prompts.KUVAN_YOU_WANT_METO_REMIND}'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(SimpleCard('Kuvan Welcoome', speak_output))
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class CreateReminderIntentHandler(AbstractRequestHandler):
    """Handler for IAmTakingKuvan messge."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CreateReminderIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        permissions = handler_input.request_envelope.context.system.user.permissions
        if not(permissions and permissions.consent_token):
            logger.info("user hasn't granted reminder permissions")
            return \
                handler_input.response_builder.speak("Please give permissions to set reminders using the alexa app.") \
                .set_card(AskForPermissionsConsentCard(permissions=REQUIRED_PERMISSIONS)) \
                .response

        #Get the slot data
        slots = handler_input.request_envelope.request.intent.slots
        # userMedication = slots['userMedication'].value
        medicineDosage = slots['medicineDosage'].value
        medicineFrequency = slots['medicineFrequency'].value
        medicineTime = slots['medicineTime'].value

        #set the session attributes
        session_attributes = handler_input.attributes_manager.session_attributes
        # session_attributes['userMedication'] = userMedication
        session_attributes['medicineDosage'] = medicineDosage
        session_attributes['medicineFrequency'] = medicineFrequency
        session_attributes['medicineTime'] = medicineTime

        reminder_service = handler_input.service_client_factory.get_reminder_management_service()
        try:
            now = datetime.datetime.now(pytz.timezone(TIME_ZONE_ID))
            #scheduled_time="2020-02-13T03:00:00.000"
            notification_time = datetime.datetime.today()
            times = [int(t) for t in medicineTime.split(':')]
            notification_time = notification_time.replace(hour=times[0], minute=times[1]).strftime("%Y-%m-%dT%H:%M:%S")
            
            trigger = Trigger(object_type=TriggerType.SCHEDULED_ABSOLUTE , scheduled_time=notification_time, time_zone_id=TIME_ZONE_ID, recurrence=Recurrence(freq=RecurrenceFreq.DAILY))
            text = SpokenText(locale='en-US', ssml='<speak>This is your reminder for Kuvan</speak>', text='This is your reminder for Kuvan')  
            alert_info = AlertInfo(SpokenInfo([text]))  
            push_notification = PushNotification(PushNotificationStatus.ENABLED)  
            reminder_request = ReminderRequest(notification_time, trigger, alert_info, push_notification)
        except ServiceException as e:
            logger.info("Exception encountered while creating Reminder: {}".format(e.body))
            speech_text = "Uh Oh. Looks like something went wrong."
            return handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Error while creating reminder.",str(e.body))).response

        speak_output = f'We have created {medicineFrequency} reminder at {medicineTime} for Kuvan'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_card(SimpleCard('Kuvan Reminder', speak_output))
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = CustomSkillBuilder(api_client=DefaultApiClient())  # required to use remiders
#sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(IAmTakingKuvanIntentHandler())
sb.add_request_handler(CreateReminderIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

#lambda_handler = sb.lambda_handler()
def handler(event, context):
	return sb.lambda_handler()(event, context)