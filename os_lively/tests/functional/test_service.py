#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid

from os_lively import service
from os_lively.tests.functional import base


class ServiceTestCase(base.TestCase):

    def test_smoke(self):
        service_uuid = uuid.uuid4().hex

        # Starting off, service shouldn't be UP when requesting a service that
        # hasn't yet been created
        self.assertFalse(
            service.is_up(self.cfg, uuid=service_uuid)
        )
        self.assertFalse(
            service.is_up(self.cfg, type='nova-compute', host='localhost')
        )

        # Create the service record in an UP status and validate that the
        # service is found and in an UP state
        s = service.Service()
        s.uuid = service_uuid
        s.host = 'localhost'
        s.type = 'nova-compute'
        s.region = 'us-east'
        s.status = service.Status.UP
        service.update(self.cfg, s)

        self.assertTrue(
            service.is_up(self.cfg, uuid=service_uuid)
        )
        self.assertTrue(
            service.is_up(self.cfg, type='nova-compute', host='localhost')
        )

        res = service.get_one(self.cfg, uuid=service_uuid)
        self.assertIsInstance(res, service.Service)
        self.assertEqual(service_uuid, res.uuid)
        self.assertEqual('localhost', res.host)
        self.assertEqual('nova-compute', res.type)
        self.assertEqual('us-east', res.region)

        # Set to DOWN state, service.update() the message object just retrieved
        # from service.get_one() and then verify the service is no longer in
        # the /services/by-status/UP index
        res.status = service.Status.DOWN
        service.update(self.cfg, res)
        self.assertFalse(
            service.is_up(self.cfg, uuid=service_uuid)
        )

        # Get a list of all the services in the system and ensure our service
        # is in there
        services = service.get_many(self.cfg)
        service_uuids = [s.uuid for s in services]
        self.assertIn(service_uuid, service_uuids)

        # Try filtering by wrong region
        services = service.get_many(self.cfg, region='us-west')
        service_uuids = [s.uuid for s in services]
        self.assertNotIn(service_uuid, service_uuids)

        # Try filtering by a right region
        services = service.get_many(self.cfg, region='us-east')
        service_uuids = [s.uuid for s in services]
        self.assertIn(service_uuid, service_uuids)

        # Try filtering by wrong type
        services = service.get_many(self.cfg, type='nova-conductor')
        service_uuids = [s.uuid for s in services]
        self.assertNotIn(service_uuid, service_uuids)

        # Try filtering by a right type
        services = service.get_many(self.cfg, type='nova-compute')
        service_uuids = [s.uuid for s in services]
        self.assertIn(service_uuid, service_uuids)

        # Try filtering by wrong status
        services = service.get_many(self.cfg, status=service.Status.UP)
        service_uuids = [s.uuid for s in services]
        self.assertNotIn(service_uuid, service_uuids)

        # Try filtering by a right status
        services = service.get_many(self.cfg, status=service.Status.DOWN)
        service_uuids = [s.uuid for s in services]
        self.assertIn(service_uuid, service_uuids)

        # Try filtering by wrong host
        services = service.get_many(self.cfg, host='otherhost')
        service_uuids = [s.uuid for s in services]
        self.assertNotIn(service_uuid, service_uuids)

        # Try filtering by a right host
        services = service.get_many(self.cfg, host='localhost')
        service_uuids = [s.uuid for s in services]
        self.assertIn(service_uuid, service_uuids)

        # Delete the service and verify there's no longer any record of it
        service.delete(self.cfg, uuid=service_uuid)
        res = service.get_one(self.cfg, uuid=service_uuid)
        self.assertIsNone(res)
        self.assertFalse(
            service.is_up(self.cfg, uuid=service_uuid)
        )
