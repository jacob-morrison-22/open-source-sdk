# type: ignores

from canvas_workflow_kit import events
from canvas_workflow_kit.constants import CHANGE_TYPE
from canvas_workflow_kit.internal.integration_messages import (
    ensure_patient_in_group,
    ensure_patient_not_in_group
)    
from canvas_workflow_kit.protocol import (
    STATUS_NOT_APPLICABLE,
    ClinicalQualityMeasure,
    ProtocolResult
)



class PatientGrouping(ClinicalQualityMeasure):
    """
    Protocol that updates a patients membership in a group depending on a given consent. 
    This particular example is of an opt-out based group membership.
    """

    GROUP_NAME = 'LANES'
    CONSENT_CODE = 'LANES_CONSENT'

    class Meta:
        title = 'Patient Grouping'

        version = '1.0.0'

        information = ''

        description = (
            'Protocol that updates a patients membership in a group depending on a given consent. '
            'This particular example is of an opt-out based group membership. ')

        identifiers = ['PatientGrouping']

        types = ['CQM']

        responds_to_event_types = [
            events.HEALTH_MAINTENANCE,
        ]

        authors = [
            'Canvas'
        ]

        compute_on_change_types = [
            CHANGE_TYPE.CONSENT
        ]

        funding_source = ''

        references = ['Written by Canvas']


    def has_opt_out(self) -> bool:
        consents = self.patient.consents.filter(category__code=self.CONSENT_CODE)
        
        if consents:
            state = consents[0]['state']
            return True if state == 'rejected' else False

        return False

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()
        result.status = STATUS_NOT_APPLICABLE
       
        patient_key = self.patient.patient['key']

        # Get this UUID from the api_patientgroup.externally_exposable_id field
        patient_group_uuid = 'bb0d3a51-fad4-4500-a42d-fe87079ac2c7'


        # This particular group operates on an opt-out policy, so a patient should be 
        # in the group unless they have the opt out consent
        if self.has_opt_out():
            group_update = ensure_patient_not_in_group(patient_key, patient_group_uuid)
        else:
            group_update = ensure_patient_in_group(patient_key, patient_group_uuid)

        self.set_updates([group_update])

        return result
