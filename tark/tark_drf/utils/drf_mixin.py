"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import importlib


class SerializerMixin(object):

    def set_related_fields(self, cls, **kwargs):
        many2one = getattr(cls, 'MANY2ONE_SERIALIZER', None)
        one2many = getattr(cls, 'ONE2MANY_SERIALIZER', None)
        entries = []

        if 'context' in kwargs:
            request_obj = kwargs['context']['request']
            query_params = request_obj.query_params
            if 'expand' in query_params:
                entry = query_params['expand']
                entries = entry.split(',') if entry else None
            elif 'expand_all' in query_params and query_params['expand_all'] == 'true':
                if many2one is not None:
                    entries.extend(list(many2one.keys()))
                if one2many is not None:
                    entries.extend(list(one2many.keys()))

            for entry in entries:
                entry = entry.strip()
                if many2one is not None and entry in many2one.keys():

                    if isinstance(many2one[entry], str):
                        module_name, class_name = many2one[entry].rsplit(".", 1)
                        instance_ = getattr(importlib.import_module(module_name), class_name)
                        self.fields[entry] = instance_(read_only=True)
                    else:
                        self.fields[entry] = many2one[entry](read_only=True)

                if one2many is not None and entry in one2many.keys():
                    if isinstance(one2many[entry], str):
                        module_name, class_name = one2many[entry].rsplit(".", 1)
                        instance_ = getattr(importlib.import_module(module_name), class_name)
                        self.fields[entry] = instance_(many=True, read_only=True)
                    else:
                        if entry == "exons":
                            self.fields[entry] = one2many[entry](source="exontranscript_set", many=True, read_only=True)
                        else:
                            self.fields[entry] = one2many[entry](many=True, read_only=True)
