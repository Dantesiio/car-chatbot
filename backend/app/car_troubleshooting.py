import json
from experta import *
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import re


def create_bayesian_network():
    # Define the structure of the network
    model = BayesianNetwork([
        ('Battery', 'NoStart'),
        ('Ignition', 'NoStart'),
        ('NoStart', 'CheckEngineLight'),
        ('BrakeSystem', 'BrakeFailure'),
        ('BrakePedal', 'BrakeFailure'),
        ('ElectricalSystem', 'ElectricalFailure'),
        ('Alternator', 'ElectricalFailure')
    ])

    # CPDs for starter problems
    cpd_battery = TabularCPD(variable='Battery', variable_card=2, 
                             values=[[0.8], [0.2]])  # [Functional, Faulty]
    
    cpd_ignition = TabularCPD(variable='Ignition', variable_card=2, 
                              values=[[0.7], [0.3]])  # [Functional, Faulty]
    
    cpd_no_start = TabularCPD(variable='NoStart', variable_card=2,
                              values=[[0.9, 0.6, 0.7, 0.1],
                                      [0.1, 0.4, 0.3, 0.9]],
                              evidence=['Battery', 'Ignition'],
                              evidence_card=[2, 2])

    cpd_check_engine_light = TabularCPD(variable='CheckEngineLight', variable_card=2,
                                        values=[[0.7, 0.2],
                                                [0.3, 0.8]],
                                        evidence=['NoStart'],
                                        evidence_card=[2])

    # CPDs for brake system
    cpd_brake_system = TabularCPD(variable='BrakeSystem', variable_card=2,
                                  values=[[0.85], [0.15]])  # [Functional, Faulty]

    cpd_brake_pedal = TabularCPD(variable='BrakePedal', variable_card=2,
                                 values=[[0.9], [0.1]])  # [Normal, Abnormal]

    cpd_brake_failure = TabularCPD(variable='BrakeFailure', variable_card=2,
                                   values=[[0.95, 0.6, 0.7, 0.1],
                                           [0.05, 0.4, 0.3, 0.9]],
                                   evidence=['BrakeSystem', 'BrakePedal'],
                                   evidence_card=[2, 2])

    # CPDs for electrical system
    cpd_electrical_system = TabularCPD(variable='ElectricalSystem', variable_card=2,
                                       values=[[0.85], [0.15]])  # [Functional, Faulty]

    cpd_alternator = TabularCPD(variable='Alternator', variable_card=2,
                                values=[[0.9], [0.1]])  # [Functional, Faulty]

    cpd_electrical_failure = TabularCPD(variable='ElectricalFailure', variable_card=2,
                                        values=[[0.95, 0.3, 0.4, 0.1],
                                                [0.05, 0.7, 0.6, 0.9]],
                                        evidence=['ElectricalSystem', 'Alternator'],
                                        evidence_card=[2, 2])

    # Add all CPDs to the model
    model.add_cpds(cpd_battery, cpd_ignition, cpd_no_start, cpd_check_engine_light,
                   cpd_brake_system, cpd_brake_pedal, cpd_brake_failure,
                   cpd_electrical_system, cpd_alternator, cpd_electrical_failure)

    # Verify that the model is valid
    model.check_model()

    return model

class CarTroubleshootingChatbot:
    def __init__(self):
        self.engine = CarTroubleshootingSystem()
        self.engine.reset()
        self.bayesian_network = create_bayesian_network()
        self.inference = VariableElimination(self.bayesian_network)
        self.current_question = None
        self.evidence = {}
        self.conversation_log = [] 
        
    def update_probabilities(self, symptom, value):
        # Complete mapping of questions to variables
        symptom_mapping = {
            'Do the Starter spins?': 'Battery',
            'Do the battery read over 12V?': 'Battery',
            'Are the terminals clean?': 'Battery',
            'Spark from coil?': 'Ignition',
            'Check Engine Light On?': 'CheckEngineLight',
            'Do the brakes feel spongy?': 'BrakeSystem',
            'Is the brake pedal firm?': 'BrakePedal',
            'Is there an electrical failure?': 'ElectricalSystem',
            'Was the Alternator tested OK?': 'Alternator'
        }
        
        # Get the corresponding variable
        bayesian_var = symptom_mapping.get(symptom)
        if bayesian_var:
            self.evidence[symptom] = int(value == 'yes')
            
            if bayesian_var == 'Battery':
                problems = self._count_battery_problems()
                self.evidence['Battery'] = 1 if problems >= 2 else 0
            elif bayesian_var in ['BrakeSystem', 'BrakePedal']:
                problems = self._count_brake_problems()
                self.evidence['BrakeFailure'] = 1 if problems >= 1 else 0
            elif bayesian_var in ['ElectricalSystem', 'Alternator']:
                problems = self._count_electrical_problems()
                self.evidence['ElectricalFailure'] = 1 if problems >= 1 else 0
            
            try:
                prob_failure = self._calculate_system_probability(bayesian_var)
                return prob_failure, bayesian_var
                    
            except Exception as e:
                return None, None
        
        return None, None

    def _count_battery_problems(self):
            problems = 0
            if 'Do the Starter spins?' in self.evidence and self.evidence['Do the Starter spins?'] == 0:
                problems += 1
            if 'Do the battery read over 12V?' in self.evidence and self.evidence['Do the battery read over 12V?'] == 0:
                problems += 1
            if 'Are the terminals clean?' in self.evidence and self.evidence['Are the terminals clean?'] == 0:
                problems += 1
            return problems

    def _count_brake_problems(self):
        problems = 0
        if 'Do the brakes feel spongy?' in self.evidence and self.evidence['Do the brakes feel spongy?'] == 1:
            problems += 1
        if 'Is the brake pedal firm?' in self.evidence and self.evidence['Is the brake pedal firm?'] == 0:
            problems += 1
        return problems

    def _count_steering_problems(self):
        problems = 0
        if 'Is the steering loose?' in self.evidence and self.evidence['Is the steering loose?'] == 1:
            problems += 1
        if 'Is the power steering working?' in self.evidence and self.evidence['Is the power steering working?'] == 0:
            problems += 1
        return problems

    def _count_electrical_problems(self):
        problems = 0
        if 'Is there an electrical failure?' in self.evidence and self.evidence['Is there an electrical failure?'] == 1:
            problems += 1
        if 'Was the Alternator tested OK?' in self.evidence and self.evidence['Was the Alternator tested OK?'] == 0:
            problems += 1
        return problems

    def _calculate_system_probability(self, bayesian_var):
        # Create a dictionary of evidence only with the variables of the Bayesian network
        bayesian_evidence = {}
        
        if bayesian_var in ['Battery', 'Ignition']:
            bayesian_evidence['Battery'] = self.evidence.get('Battery', 0)
            query_result = self.inference.query(['NoStart'], evidence=bayesian_evidence)
            prob_values = query_result.values
            prob_failure = float(prob_values[1])
            problems = self._count_battery_problems()
            
        elif bayesian_var in ['BrakeSystem', 'BrakePedal']:
            bayesian_evidence['BrakeFailure'] = self.evidence.get('BrakeFailure', 0)
            query_result = self.inference.query(['BrakeFailure'], evidence=bayesian_evidence)
            prob_values = query_result.values
            prob_failure = float(prob_values[1])
            problems = self._count_brake_problems()
            
        elif bayesian_var in ['ElectricalSystem', 'Alternator']:
            query_result = self.inference.query(['ElectricalFailure'], evidence=self.evidence)
            prob_values = query_result.values
            prob_failure = float(prob_values[1])
            problems = self._count_electrical_problems()
        
        # Adjust the probability based on the number of problems
        if problems == 1:
            prob_failure = (prob_failure + 0.3) / 2
        elif problems >= 2:
            prob_failure = (prob_failure + 0.7) / 2
            
        return prob_failure

    def diagnose(self, message):
    # Normalize and clean the input message
        message = message.lower()
        message = re.sub(r'[^\w\s]', '', message)

        # Define known symptoms and corresponding keywords
        symptoms = {
            # Starter-related issues
            'no_start': ["not starting", "no start", "wont start", "won't start", "doesn't start", "does not start", "car won't turn on"],
            'car_stall': ["car stall", "car start and stall", "car stops", "the car starts and then stalls"],
            # Unusual noise
            'unusual_noise': ["unusual noise", "strange noise", "weird sound", "clicking noise", "knocking noise", "noise in car"],
            'tick_noise': ["tick noise", "unusual tick noises", "ticks on engine", "ticks", "tick when moving"],
            # Overheating and leaks
            'streaming': ["streaming", "stream", "smoking", "stream from engine"],
            'leaking': ["leaking", "leak", "dropping"],
            # Brakes and electrical systems
            'brakes_problem': ["brakes problems", "brakes", "brake", "dont have brakes", "car doesn't stop"],
            'electric_problems': ["electric problems", "electric problem", "electric", "electronic", "wire problems"]
        }

        # Check if the message matches a known symptom
        for symptom, phrases in symptoms.items():
            for phrase in phrases:
                if phrase in message:
                    # Handle symptom-specific logic
                    if symptom == 'no_start':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(starter_cranks='no'))
                        self.evidence = {}
                        self.engine.run()
                        return self.process_questions()
                    if symptom == 'car_stall':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(starter_cranks='yes'))
                        self.engine.run()
                        return self.process_questions()
                    if symptom == 'unusual_noise':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(clunk_or_singletick='yes'))
                        self.engine.run()
                        return self.process_questions()
                    if symptom == 'tick_noise':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(clunk_or_singletick='no'))
                        self.engine.run()
                        return self.process_questions()
                    if symptom == 'streaming':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(streaming_or_leak='yes'))
                        self.engine.run()
                        return self.process_questions()
                    if symptom == 'leaking':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(streaming_or_leak='no'))
                        self.engine.run()
                        return self.process_questions()
                    if symptom == 'brakes_problem':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(brakes_failure='yes'))
                        self.engine.run()
                        return self.process_questions()
                    if symptom == 'electric_problems':
                        self.engine.reset()
                        self.engine.declare(CarDiagnosis(electric_problem='yes'))
                        self.engine.run()
                        return self.process_questions()

        # Process the message as an answer to the current question
        if self.current_question:
            prob, bayesian_var = self.update_probabilities(self.current_question, message)

            # Declare the fact based on the current response
            expected_fact = self.engine.expected_facts.get(self.current_question)
            if expected_fact:
                self.engine.declare(CarDiagnosis(**{expected_fact: message}))
                self.engine.run()

            next_question = self.process_questions()
            probability_message = ""

            if prob:
                # Map Bayesian variables to system names
                system_names = {
                    'Battery': 'Battery System',
                    'Ignition': 'Ignition System',
                    'BrakeSystem': 'Brake System',
                    'BrakePedal': 'Brake System',
                    'ElectricalSystem': 'Electrical System',
                    'Alternator': 'Electrical System'
                }
                system_name = system_names.get(bayesian_var, 'System')

                if prob > 0.7:
                    probability_message = f"High probability ({prob:.2f}) of failure in the {system_name}. Immediate inspection recommended.\n"
                elif prob > 0.5:
                    probability_message = f"Moderate to high probability ({prob:.2f}) of failure in the {system_name}.\n"
                elif prob > 0.3:
                    probability_message = f"Some indicators of possible failure ({prob:.2f}) in the {system_name}.\n"

            if "Diagnostic:" in next_question:
                self.current_question = None
                self.evidence = {}
                return f"{probability_message} {next_question}\nDiagnosis completed. Is there any other issue you'd like to discuss?"
            else:
                return f"{probability_message} {next_question}"

        # Handle generic responses
        responds = {
            'no': ["no", "nooo", "negative", "maybe not", "it not", "nn", "nah", "nope", "n"],
            'yes': ["yes", "affirmative", "obscurse", "yy", "yesy", "yup", "yeah", "yep", "y"]
        }

        for respond, phrases in responds.items():
            for phrase in phrases:
                if phrase in message:
                    return self.respond_to_input(message)

        # If no valid symptom or answer was detected
        return "Sorry, I don't understand the problem. Could you describe the symptom in another way?"


    def process_questions(self):
        """
        Retrieves the next question from the list of questions generated by the engine.
        """
        questions = self.engine.get_questions()
        if questions:
            self.current_question = questions[0]
            return questions.pop(0)
        return "There are no more questions."

    def respond_to_input(self, message):
        """
        Processes the user's input as a response to the current question.
        """
        # If there is no current question, ask the user to describe the issue
        if not self.current_question:
            return "There are no pending questions. Please describe the problem you are experiencing with your vehicle."

        # Define mappings for 'yes' and 'no' responses
        responds = {
            'no': ["no", "negative", "maybe not", "it not"],
            'yes': ["yes", "affirmative", "of course", "yeah"]
        }

        # Determine if the response is 'yes' or 'no'
        response = None
        for answer, phrases in responds.items():
            if any(phrase in message.lower() for phrase in phrases):
                response = answer
                break

        if response:
            # Update the rule engine with the response
            expected_fact = self.engine.expected_facts.get(self.current_question)
            if expected_fact:
                self.engine.declare(CarDiagnosis(**{expected_fact: response}))
                self.engine.run()
                return self.process_questions()
        
        return "Please respond with 'yes' or 'no' to the question."



class CarDiagnosis(Fact):
    pass

class CarTroubleshootingSystem(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.questions = []
        self.expected_facts = {}

    def get_questions(self):
        return self.questions

    def clear_questions(self):
        self.questions.clear()

    # Start Problem

    @Rule(CarDiagnosis(start_problem='yes'))
    def start_problem(self):
        message = 'Do the Starter cranks?'
        self.questions.append(message)
        self.expected_facts[message] = 'starter_cranks'

    @Rule(CarDiagnosis(starter_cranks='no'))
    def starter_cranks_no(self):
        message = "Do the Starter spins?"
        self.questions.append(message)
        self.expected_facts[message] = 'starter_spins'

    @Rule(CarDiagnosis(starter_spins='yes'))
    def starter_spins_yes(self):
        self.questions.append("Diagnostic: Inspect the solenoid for being stuck or not powered. Check the flywheel for missing teeth.")

    @Rule(CarDiagnosis(starter_spins='no'))
    def starter_spins_no(self):
        message = "Do the battery read over 12V?"
        self.questions.append(message)
        self.expected_facts[message] = 'battery_over_12v'

    @Rule(CarDiagnosis(battery_over_12v='yes'))
    def battery_over_12v_yes(self):
        message = "Are the terminals clean?"
        self.questions.append(message)
        self.expected_facts[message] = 'cleaned_terminals'

    @Rule(CarDiagnosis(cleaned_terminals='yes'))
    def cleaned_terminals_yes(self):
        self.questions.append("Diagnostic: Place the car in park or neutral, use a heavy jumper or screwdriver to bypass the starter relay solenoid, and test the starter.")

    @Rule(CarDiagnosis(cleaned_terminals='no'))
    def cleaned_terminals_no(self):
        self.questions.append("Diagnostic: Clean the battery terminals, connectors, and the engine ground for a better electrical connection.")

    @Rule(CarDiagnosis(battery_over_12v='no'))
    def battery_over_12v_no(self):
        self.questions.append("Diagnostic: Attempt to jump-start or pop-start the car and verify if the battery charges correctly.")

    @Rule(CarDiagnosis(starter_cranks='yes'))
    def starter_cranks_yes(self):
        message = "Do the engine fires?"
        self.questions.append(message)
        self.expected_facts[message] = 'engine_fires'

    @Rule(CarDiagnosis(engine_fires='yes'))
    def engine_fires_yes(self):
        message = "Starts and stalls?"
        self.questions.append(message)
        self.expected_facts[message] = 'starts_and_stalls'

    @Rule(CarDiagnosis(starts_and_stalls='no'))
    def starts_and_stalls_no(self):
        self.questions.append("Diagnostic: Inspect the ignition timing and check for fuel-related issues.")

    @Rule(CarDiagnosis(starts_and_stalls='yes'))
    def starts_and_stalls_yes(self):
        message = "Check OBD, blink code?"
        self.questions.append(message)
        self.expected_facts[message] = 'check_obd'

    @Rule(CarDiagnosis(check_obd='yes'))
    def check_obd_yes(self):
        message = "Stall on key release to run?"
        self.questions.append(message)
        self.expected_facts[message] = 'stalls_on_key_release'

    @Rule(CarDiagnosis(stalls_on_key_release='yes'))
    def stalls_on_key_release_yes(self):
        self.questions.append("Diagnostic: Inspect the ignition run circuit or check for column key switch failure using a multimeter.")

    @Rule(CarDiagnosis(stalls_on_key_release='no'))
    def stalls_on_key_release_no(self):
        message = "Stalls in rain?"
        self.questions.append(message)
        self.expected_facts[message] = 'stalls_in_rain'

    @Rule(CarDiagnosis(stalls_in_rain='yes'))
    def stalls_in_rain_yes(self):
        self.questions.append("Diagnostic: Check for a cracked coil or distributor and inspect for visible electrical arcing in the dark.")

    @Rule(CarDiagnosis(stalls_in_rain='no'))
    def stalls_in_rain_no(self):
        message = "Stalls warm?"
        self.questions.append(message)
        self.expected_facts[message] = 'stalls_warm'

    @Rule(CarDiagnosis(stalls_warm='yes'))
    def stalls_warm_yes(self):
        self.questions.append("Diagnostic: Adjust the idle, clean the fuel filter, check the fuel pump output, and inspect for vacuum leaks or sensor failures.")

    @Rule(CarDiagnosis(stalls_warm='no'))
    def stalls_warm_no(self):
        self.questions.append("Diagnostic: For cold-start stalling, check for a stuck choke, EGR valve, or vacuum leaks.")

    @Rule(CarDiagnosis(check_obd='no'))
    def check_obd_no(self):
        self.questions.append("Diagnostic: Use an OBD or OBD II scanner or check for blink codes to diagnose the issue.")

    @Rule(CarDiagnosis(engine_fires='no'))
    def engine_fires_no(self):
        message = "Spark to plugs?"
        self.questions.append(message)
        self.expected_facts[message] = 'spark_to_plugs'

    @Rule(CarDiagnosis(spark_to_plugs='yes'))
    def spark_to_plugs_yes(self):
        message = "Fuel to filter?"
        self.questions.append(message)
        self.expected_facts[message] = 'fuel_to_filter'

    @Rule(CarDiagnosis(fuel_to_filter='no'))
    def fuel_to_filter_no(self):
        self.questions.append("Diagnostic: Investigate vapor lock, fuel pump issues, or potential blockages in the system.")

    @Rule(CarDiagnosis(fuel_to_filter='yes'))
    def fuel_to_filter_yes(self):
        message = "Fuel injected?"
        self.questions.append(message)
        self.expected_facts[message] = 'fuel_injected'

    @Rule(CarDiagnosis(fuel_injected='no'))
    def fuel_injected_no(self):
        self.questions.append("Diagnostic: Use starter spray on the carburetor or throttle while keeping it open.")

    @Rule(CarDiagnosis(fuel_injected='yes'))
    def fuel_injected_yes(self):
        self.questions.append("Diagnostic: For single-point systems, inspect the throttle body. For multipoint systems, refer to the specific model's diagnostic procedures.")

    @Rule(CarDiagnosis(spark_to_plugs='no'))
    def spark_to_plugs_no(self):
        message = "Spark from coil?"
        self.questions.append(message)
        self.expected_facts[message] = 'spark_from_coil'

    @Rule(CarDiagnosis(spark_from_coil='no'))
    def spark_from_coil_no(self):
        message = "12V+ at coil primary?"
        self.questions.append(message)
        self.expected_facts[message] = 'coil_over_12v'

    @Rule(CarDiagnosis(coil_over_12v='no'))
    def coil_over_12v_no(self):
        self.questions.append("Diagnostic: Check the ignition system wiring and the voltage regulator.")

    @Rule(CarDiagnosis(coil_over_12v='yes'))
    def coil_over_12v_yes(self):
        self.questions.append("Diagnostic: Test the coil for internal shorts and verify the resistance of the secondary output wire.")

    @Rule(CarDiagnosis(spark_from_coil='yes'))
    def spark_from_coil_yes(self):
        message = "Mechanical distributor?"
        self.questions.append(message)
        self.expected_facts[message] = 'mechanical_distributor'

    @Rule(CarDiagnosis(mechanical_distributor='no'))
    def mechanical_distributor_no(self):
        self.questions.append("Diagnostic: For electronic distributors, consult the model's manual for advanced diagnostic procedures.")

    @Rule(CarDiagnosis(mechanical_distributor='yes'))
    def mechanical_distributor_yes(self):
        self.questions.append("Diagnostic: Inspect the condenser, points, magnetic pickup, rotor, or distributor cap for any damage.")
    
    # Car noises 

    @Rule(CarDiagnosis(clunk_or_singletick='yes'))
    def clunk_or_singletick_yes(self):
        message = "Noise on bumps only?"
        self.questions.append(message)
        self.expected_facts[message] = 'noise_on_bumps'

    @Rule(CarDiagnosis(noise_on_bumps='yes'))
    def noise_on_bumps_yes(self):
        self.questions.append("Diagnostic: Inspect the struts, shocks, springs, and frame welds for any damage or wear.")

    @Rule(CarDiagnosis(noise_on_bumps='no'))
    def noise_on_bumps_no(self):
        self.questions.append("Diagnostic: Examine the ball joints, brake components, rack and tie rod ends, and motor mounts for potential issues.")

    @Rule(CarDiagnosis(clunk_or_singletick='no'))
    def clunk_or_singletick_no(self):
        message = "Only ticks when moving?"
        self.questions.append(message)
        self.expected_facts[message] = 'ticks_moving'

    @Rule(CarDiagnosis(ticks_moving='no'))
    def ticks_moving_no(self):
        message = "Preliminary diagnostic: Try to localize the tick using a hearing tube or long screwdriver. Now respond, do you hear only ticks when cold?"
        self.questions.append(message)
        self.expected_facts[message] = 'ticks_on_cold'

    @Rule(CarDiagnosis(ticks_on_cold='yes'))
    def ticks_on_cold_yes(self):
        self.questions.append("Diagnostic: Inspect the exhaust pipe forward of the catalytic converter for leaks. Also, check for lifter rap on the valve cover.")

    @Rule(CarDiagnosis(ticks_on_cold='no'))
    def ticks_on_cold_no(self):
        message = "Windshield wipers, radio off?"
        self.questions.append(message)
        self.expected_facts[message] = 'windshield_or_radio'

    @Rule(CarDiagnosis(windshield_or_radio='no'))
    def windshield_or_radio_no(self):
        self.questions.append("Diagnostic: Double-check simple causes, such as windshield wipers or other minor components causing noise.")

    @Rule(CarDiagnosis(windshield_or_radio='yes'))
    def windshield_or_radio(self):
        self.questions.append("Diagnostic: Look for pulley wobble, inspect belts, and check for an exhaust manifold leak. Use assistance to localize the sound in the engine.")

    @Rule(CarDiagnosis(ticks_moving='yes'))
    def ticks_moving_yes(self):
        message = "Ticks rolling in neutral?"
        self.questions.append(message)
        self.expected_facts[message] = 'ticks_on_neutral'

    @Rule(CarDiagnosis(ticks_on_neutral='no'))
    def ticks_on_neutral_no(self):
        message = "Ticks only in reverse?"
        self.questions.append(message)
        self.expected_facts[message] = 'ticks_on_reverse'

    @Rule(CarDiagnosis(ticks_on_reverse='no'))
    def ticks_on_reverse_no(self):
        self.questions.append("Diagnostic: Check for transmission-related issues such as a ticking sound caused by a transmission fluid filter.")

    @Rule(CarDiagnosis(ticks_on_reverse='yes'))
    def ticks_on_reverse_yes(self):
        self.questions.append("Diagnostic: Check the rear brake adjuster and ensure the parking brake is fully released.")

    @Rule(CarDiagnosis(ticks_on_neutral='yes'))
    def ticks_on_neutral_yes(self):
        message = "Frequency drops on shifts?"
        self.questions.append(message)
        self.expected_facts[message] = 'drop_on_shifts'

    @Rule(CarDiagnosis(drop_on_shifts='yes'))
    def drop_on_shifts_yes(self):
        self.declare(CarDiagnosis(ticks_moving='no'))

    @Rule(CarDiagnosis(drop_on_shifts='no'))
    def drop_on_shifts_no(self):
        message = "Only ticks in turns, curves?"
        self.questions.append(message)
        self.expected_facts[message] = 'ticks_on_curves'

    @Rule(CarDiagnosis(ticks_on_curves='yes'))
    def ticks_on_curves_yes(self):
        self.questions.append("Diagnostic: Inspect the CV joint or verify if the tire size is too large for the wheel well.")

    @Rule(CarDiagnosis(ticks_on_curves='no'))
    def ticks_on_curves_no(self):
        message = "Preliminary diagnostic: Tick is likely related to wheel rotation. Now respond, did you recently change tires?"
        self.questions.append(message)
        self.expected_facts[message] = 'changed_tires'

    @Rule(CarDiagnosis(changed_tires='yes'))
    def changed_tires_yes(self):
        self.questions.append("Diagnostic: STOP DRIVING IMMEDIATELY! Ensure all wheel lugs are properly tightened.")

    @Rule(CarDiagnosis(changed_tires='no'))
    def changed_tires_no(self):
        message = "Removed hubcaps?"
        self.questions.append(message)
        self.expected_facts[message] = 'removed_hubcaps'

    @Rule(CarDiagnosis(removed_hubcaps='no'))
    def removed_hubcaps_no(self):
        self.questions.append("Diagnostic: Remove hubcaps and inspect for loose wire retainers or pebbles causing the ticking noise.")

    @Rule(CarDiagnosis(removed_hubcaps='yes'))
    def removed_hubcaps_yes(self):
        message = "Inspect tire treads?"
        self.questions.append(message)
        self.expected_facts[message] = 'inspect_tire_treads'

    @Rule(CarDiagnosis(inspect_tire_treads='no'))
    def inspect_tire_treads_no(self):
        self.questions.append("Diagnostic: Check for nails or stones embedded in the tire treads.")

    @Rule(CarDiagnosis(inspect_tire_treads='yes'))
    def inspect_tire_treads_yes(self):
        message = "Ticks only at low speed?"
        self.questions.append(message)
        self.expected_facts[message] = 'ticks_on_lowspeed'

    @Rule(CarDiagnosis(ticks_on_lowspeed='yes'))
    def ticks_on_lowspeed_yes(self):
        self.questions.append("Diagnostic: Inspect bolted wheel covers for any loose components.")

    @Rule(CarDiagnosis(ticks_on_lowspeed='no'))
    def ticks_on_lowspeed_no(self):
        self.questions.append("Diagnostic: The issue could be brake pads ticking on a warped rotor. Check axles for rubbing or other damage.")

 # Car engine

    @Rule(CarDiagnosis(streaming_or_leak='no'))
    def streaming_or_leak_no(self):
        message = "Smell antifreeze?"
        self.questions.append(message)
        self.expected_facts[message] = 'smell_antifreeze'

    @Rule(CarDiagnosis(smell_antifreeze='yes'))
    def smell_antifreeze_yes(self):
        self.questions.append("Diagnostic: There is likely a leak, even if not immediately visible. Check thoroughly.")

    @Rule(CarDiagnosis(smell_antifreeze='no'))
    def smell_antifreeze_no(self):
        message = "Needle gauge?"
        self.questions.append(message)
        self.expected_facts[message] = 'needle_gauge'

    @Rule(CarDiagnosis(needle_gauge='no'))
    def needle_gauge_no(self):
        message = "Check the owner's manual for special light behavior. Now respond, is the antifreeze level good?"
        self.questions.append(message)
        self.expected_facts[message] = 'antifreeze_level_good'

    @Rule(CarDiagnosis(antifreeze_level_good='no'))
    def antifreeze_level_good_no(self):
        self.questions.append("Diagnostic: Refill with a 50/50 mix of antifreeze, but ensure not to overfill.")

    @Rule(CarDiagnosis(needle_gauge='yes'))
    def needle_gauge_yes(self):
        message = "Does the needle return to normal?"
        self.questions.append(message)
        self.expected_facts[message] = 'ng_return_normal'

    @Rule(CarDiagnosis(ng_return_normal='yes'))
    def ng_return_normal_yes(self):
        self.questions.append("Diagnostic: Check for a sticking thermostat, airlock, or incorrect temperature thermostat.")

    @Rule(CarDiagnosis(ng_return_normal='no'))
    def ng_return_normal_no(self):
        self.declare(CarDiagnosis(needle_gauge='no'))

    @Rule(CarDiagnosis(antifreeze_level_good='yes'))
    def antifreeze_level_good_yes(self):
        message = "Is the fan operating?"
        self.questions.append(message)
        self.expected_facts[message] = 'fan_operate'

    @Rule(CarDiagnosis(fan_operate='no'))
    def fan_operate_no(self):
        self.questions.append("Diagnostic: Test the fan motor with a direct connection, check the fan fuse, and replace the temperature sensor if needed.")

    @Rule(CarDiagnosis(fan_operate='yes'))
    def fan_operate_yes(self):
        message = "Is the coolant flow good?"
        self.questions.append(message)
        self.expected_facts[message] = 'flow_good'

    @Rule(CarDiagnosis(flow_good='no'))
    def flow_good_no(self):
        self.questions.append("Diagnostic: Investigate for pump failure or a blockage in the cooling system.")

    @Rule(CarDiagnosis(flow_good='yes'))
    def flow_good_yes(self):
        message = "Has the engine been flushed?"
        self.questions.append(message)
        self.expected_facts[message] = 'flushed_engine'

    @Rule(CarDiagnosis(flushed_engine='no'))
    def flushed_engine_no(self):
        self.questions.append("Diagnostic: Flush the engine using a kit, cleaning solution, and a garden hose. Refill with fresh 50/50 antifreeze.")

    @Rule(CarDiagnosis(flushed_engine='yes'))
    def flushed_engine_yes(self):
        message = "Has the thermostat been checked?"
        self.questions.append(message)
        self.expected_facts[message] = 'check_thermostat'

    @Rule(CarDiagnosis(check_thermostat='no'))
    def check_thermostat_no(self):
        self.questions.append("Diagnostic: Test the thermostat in boiling water to ensure it opens, or replace it outright.")

    @Rule(CarDiagnosis(check_thermostat='yes'))
    def check_thermostat_yes(self):
        message = "Has the timing been checked?"
        self.questions.append(message)
        self.expected_facts[message] = 'check_timing'

    @Rule(CarDiagnosis(check_timing='yes'))
    def check_timing_yes(self):
        self.questions.append("Diagnostic: Occasional overheating may indicate overdriving. Otherwise, improper thermostat installation is likely.")

    @Rule(CarDiagnosis(check_timing='no'))
    def check_timing_no(self):
        self.questions.append("Diagnostic: Incorrect ignition timing could be causing overheating.")

    @Rule(CarDiagnosis(streaming_or_leak='yes'))
    def streaming_or_leak_yes(self):
        message = "Is the cap steaming?"
        self.questions.append(message)
        self.expected_facts[message] = 'cap_steaming'

    @Rule(CarDiagnosis(cap_steaming='yes'))
    def cap_steaming_yes(self):
        self.questions.append("Diagnostic: The pressure release is working correctly. Check the antifreeze level in the overflow tank.")

    @Rule(CarDiagnosis(cap_steaming='no'))
    def cap_steaming_no(self):
        message = "Is the overflow dripping?"
        self.questions.append(message)
        self.expected_facts[message] = 'overflow_dripping'

    @Rule(CarDiagnosis(overflow_dripping='yes'))
    def overflow_dripping_yes(self):
        self.questions.append("Diagnostic: This indicates the engine is overheating or the cooling system is overfilled.")

    @Rule(CarDiagnosis(overflow_dripping='no'))
    def overflow_dripping_no(self):
        message = "Is the radiator leaking?"
        self.questions.append(message)
        self.expected_facts[message] = 'radiator_leak'

    @Rule(CarDiagnosis(radiator_leak='yes'))
    def radiator_leak_yes(self):
        self.questions.append("Diagnostic: A radiator leak could lead to overheating. Use a stop-leak product or repair/replace the radiator.")

    @Rule(CarDiagnosis(radiator_leak='no'))
    def radiator_leak_no(self):
        message = "Is there a hose leak?"
        self.questions.append(message)
        self.expected_facts[message] = 'hose_leak'

    @Rule(CarDiagnosis(hose_leak='yes'))
    def hose_leak_yes(self):
        self.questions.append("Diagnostic: Replace the hose or shorten and reclamp if the leak is near a clamp.")

    @Rule(CarDiagnosis(hose_leak='no'))
    def hose_leak_no(self):
        message = "Is there an engine leak?"
        self.questions.append(message)
        self.expected_facts[message] = 'engine_leak'

    @Rule(CarDiagnosis(engine_leak='no'))
    def engine_leak_no(self):
        message = "Is there a heater core leak?"
        self.questions.append(message)
        self.expected_facts[message] = 'heatercore_leak'

    @Rule(CarDiagnosis(heatercore_leak='no'))
    def heatercore_leak_no(self):
        self.declare(CarDiagnosis(antifreeze_level_good='yes'))

    @Rule(CarDiagnosis(heatercore_leak='yes'))
    def heatercore_leak_yes(self):
        self.questions.append("Diagnostic: Inspect heater core hoses, perform a pressure test, and repair or replace if necessary.")

    @Rule(CarDiagnosis(engine_leak='yes'))
    def engine_leak_yes(self):
        message = "Is the water pump leaking?"
        self.questions.append(message)
        self.expected_facts[message] = 'water_pump'

    @Rule(CarDiagnosis(water_pump='yes'))
    def water_pump_yes(self):
        self.questions.append("Diagnostic: A leaking water pump almost always indicates pump failure. Replace it.")

    @Rule(CarDiagnosis(water_pump='no'))
    def water_pump_no(self):
        self.questions.append("Diagnostic: Remove the leaking component and reinstall with a new gasket.")

    # Brake fail
    @Rule(CarDiagnosis(brakes_failure='yes'))
    def brakes_failure(self):
        message = "Do the brakes stop the car?"
        self.questions.append(message)
        self.expected_facts[message] = 'brakes_stop_car'

    @Rule(CarDiagnosis(brakes_stop_car='no'))
    def brakes_stop_car_no(self):
        message = "Is the pedal to the floor?"
        self.questions.append(message)
        self.expected_facts[message] = 'pedal_to_floor'

    @Rule(CarDiagnosis(pedal_to_floor='yes'))
    def pedal_to_floor_yes(self):
        message = "Is the brake fluid level OK?"
        self.questions.append(message)
        self.expected_facts[message] = 'brake_fluid_ok'

    @Rule(CarDiagnosis(brake_fluid_ok='yes'))
    def brake_fluid_ok_yes(self):
        message = "Is the brake warning light on?"
        self.questions.append(message)
        self.expected_facts[message] = 'brake_warning_light'

    @Rule(CarDiagnosis(brake_warning_light='yes'))
    def brake_warning_light_yes(self):
        self.questions.append("Diagnostic: If the parking brake is released, check for power booster problems or anti-lock brake system failure.")

    @Rule(CarDiagnosis(brake_warning_light='no'))
    def brake_warning_light_no(self):
        self.questions.append("Diagnostic: Issue likely related to power assist. Refer to the service manual.")

    @Rule(CarDiagnosis(brake_fluid_ok='no'))
    def brake_fluid_ok_no(self):
        self.questions.append("Diagnostic: Refill brake fluid to the appropriate level. If brakes feel soft, bleed the brake lines as per the service manual.")

    @Rule(CarDiagnosis(pedal_to_floor='no'))
    def pedal_to_floor_no(self):
        self.questions.append("Diagnostic: Check for pedal linkage binding, frozen or glazed calipers, pinched brake lines, or brake booster failure.")

    @Rule(CarDiagnosis(brakes_stop_car='yes'))
    def brakes_stop_car_yes(self):
        message = "Is there a parking brake failure?"
        self.questions.append(message)
        self.expected_facts[message] = 'parking_brake_failure'

    @Rule(CarDiagnosis(parking_brake_failure='yes'))
    def parking_brake_failure_yes(self):
        message = "Are the rear wheels locked?"
        self.questions.append(message)
        self.expected_facts[message] = 'rear_wheel_locked'

    @Rule(CarDiagnosis(rear_wheel_locked='yes'))
    def rear_wheel_locked_yes(self):
        self.questions.append("Diagnostic: Check for spring return failure or rusted/bound cable.")

    @Rule(CarDiagnosis(rear_wheel_locked='no'))
    def rear_wheel_locked_no(self):
        message = "Does the parking brake ratchet without force?"
        self.questions.append(message)
        self.expected_facts[message] = 'ratchets_without_force'

    @Rule(CarDiagnosis(ratchets_without_force='yes'))
    def ratchets_without_force_yes(self):
        self.questions.append("Diagnostic: Cable may be stretched, broken, or the adjuster could be frozen.")

    @Rule(CarDiagnosis(ratchets_without_force='no'))
    def ratchets_without_force_no(self):
        self.questions.append("Diagnostic: Shoes may be worn out, glazed, or contaminated with fluid.")

    @Rule(CarDiagnosis(parking_brake_failure='no'))
    def parking_brake_failure_no(self):
        message = "Do the wheels drag too much?"
        self.questions.append(message)
        self.expected_facts[message] = 'wheels_drag'

    @Rule(CarDiagnosis(wheels_drag='yes'))
    def wheels_drag_yes(self):
        self.questions.append("Diagnostic: Check for a stuck piston, hydraulic lock, over-adjusted drum shoes, or warped rotor.")

    @Rule(CarDiagnosis(wheels_drag='no'))
    def wheels_drag_no(self):
        message = "Do you need to mash the brakes?"
        self.questions.append(message)
        self.expected_facts[message] = 'mash_brakes'

    @Rule(CarDiagnosis(mash_brakes='yes'))
    def mash_brakes_yes(self):
        message = "Does it happen only after turning?"
        self.questions.append(message)
        self.expected_facts[message] = 'after_turning'

    @Rule(CarDiagnosis(after_turning='yes'))
    def after_turning_yes(self):
        self.questions.append("Diagnostic: Inspect front wheel bearings, axle nuts, and wheel lugs for looseness.")

    @Rule(CarDiagnosis(after_turning='no'))
    def after_turning_no(self):
        self.questions.append("Diagnostic: Check for air in the brake system or a fluid leak.")

    @Rule(CarDiagnosis(mash_brakes='no'))
    def mash_brakes_no(self):
        message = "Are the brakes making noises?"
        self.questions.append(message)
        self.expected_facts[message] = 'making_noises'

    @Rule(CarDiagnosis(making_noises='yes'))
    def making_noises_yes(self):
        message = "Are the noises squealing?"
        self.questions.append(message)
        self.expected_facts[message] = 'squealing'

    @Rule(CarDiagnosis(squealing='yes'))
    def squealing_yes(self):
        self.questions.append("Diagnostic: Inspect pads and shoes for wear or foreign objects embedded in them.")

    @Rule(CarDiagnosis(squealing='no'))
    def squealing_no(self):
        message = "Are there clunks?"
        self.questions.append(message)
        self.expected_facts[message] = 'clunks'

    @Rule(CarDiagnosis(clunks='yes'))
    def clunks_yes(self):
        self.questions.append("Diagnostic: Check for loose caliper bolts or suspension problems.")

    @Rule(CarDiagnosis(clunks='no'))
    def clunks_no(self):
        message = "Is there scraping or grinding?"
        self.questions.append(message)
        self.expected_facts[message] = 'scraping_or_grinding'

    @Rule(CarDiagnosis(scraping_or_grinding='yes'))
    def scraping_or_grinding_yes(self):
        self.questions.append("Diagnostic: Broken pads, excessive wear, or damaged shoe facing could be the issue.")

    @Rule(CarDiagnosis(scraping_or_grinding='no'))
    def scraping_or_grinding_no(self):
        message = "Are there rattles?"
        self.questions.append(message)
        self.expected_facts[message] = 'rattles'

    @Rule(CarDiagnosis(rattles='yes'))
    def rattles_yes(self):
        self.questions.append("Diagnostic: Check for missing or incorrectly installed anti-rattle clips on disc pads.")

    @Rule(CarDiagnosis(rattles='no'))
    def rattles_no(self):
        self.questions.append("Diagnostic: Look for chirps or ticks that increase with speed, often caused by rotor warp or run-out.")

    @Rule(CarDiagnosis(making_noises='no'))
    def making_noises_no(self):
        message = "Do the brakes pull to one side?"
        self.questions.append(message)
        self.expected_facts[message] = 'brakes_pull'

    @Rule(CarDiagnosis(brakes_pull='yes'))
    def brakes_pull_yes(self):
        self.questions.append("Diagnostic: Check for a stuck or cocked piston, air or crimped line, or master cylinder issues on the front brakes.")

    @Rule(CarDiagnosis(brakes_pull='no'))
    def brakes_pull_no(self):
        message = "Are the brakes jerky or pulsing?"
        self.questions.append(message)
        self.expected_facts[message] = 'jerky_or_pulsing'

    @Rule(CarDiagnosis(jerky_or_pulsing='yes'))
    def jerky_or_pulsing_yes(self):
        self.questions.append("Diagnostic: Investigate anti-lock brake system issues or deformed drums/rotors (test using the parking brake).")

    @Rule(CarDiagnosis(jerky_or_pulsing='no'))
    def jerky_or_pulsing_no(self):
        message = "Is braking hard?"
        self.questions.append(message)
        self.expected_facts[message] = 'hard_braking'

    @Rule(CarDiagnosis(hard_braking='yes'))
    def hard_braking_yes(self):
        self.questions.append("Diagnostic: Inspect for worn pads/shoes, a stuck piston, or power boost problems.")

    @Rule(CarDiagnosis(hard_braking='no'))
    def hard_braking_no(self):
        self.questions.append("Diagnostic: If the brake warning light is on and the parking brake is released, consult the service manual for error codes.")