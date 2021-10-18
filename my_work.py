import os
import json
import datetime
import copy

class MyWork:
    def __init__(self, path):
        assert type(path) == str
        self.path = path 
        self.works = self.read_works()
        # read work
    def read_works(self,):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                data = json.load(f)
            return  data
        else:
            return []
    def get_last_id(self):
        if len(self.works)>=1:
            last_id = self.works[-1]['id']
            return int(last_id)
        else:
            return 0

    def add_works(self, assigned_by, assigned_to, title, *description):
        date = datetime.datetime.now()
        id = self.get_last_id() + 1
        des = ''
        for d in description:
            des += d + ' '
        obj = {
            'id': id,
            'date': str(date),
            'assigned_by': assigned_by,
            'assigned_to': assigned_to,
            'title': title,
            'description': des,
            'status': 'pending',
        }
        self.works.append(obj)
        # write 
        with open(self.path, 'w') as f:
            json.dump(self.works, f)
    def update_status_work(self, work_id,status):
        work_id = int(work_id)
        w_ind = None
        for i, work in enumerate(self.works):
            if work_id == int(work['id']):
                w_ind = i
                break
        if w_ind is not None:
            # update
            work = copy.deepcopy(self.works[w_ind])
            work['status'] = str(status)
            self.works[w_ind] = work
            # write 
            with open(self.path, 'w') as f:
                json.dump(self.works, f)
            return True
        else:
            return False
            
    def get_works(self, ):
        return self.works

    def del_works(self, id):
        id = int(id)
        rm_ind = None
        for i, work in enumerate(self.works):
            if id == int(work['id']):
                rm_ind = i 
                break

        if rm_ind is not None:
            self.works.remove(self.works[i])
            #write
            with open(self.path, 'w') as f:
                json.dump(self.works, f)
            return True
        else:
            return False
