from django.db import models

class Voter(models.Model):
    ''' 
    based on newton_voters.csv structure.
    '''

    voter_id = models.CharField(max_length=20)  # Changed from IntegerField since it contains letters
    last_name = models.TextField()
    first_name = models.TextField()
    
    street_number = models.CharField(max_length=10)
    street_name = models.TextField()
    apartment_number = models.CharField(max_length=10, blank=True)
    zip_code = models.CharField(max_length=10)
    
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=2)
    precinct_number = models.CharField(max_length=10)
    
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    
    voter_score = models.IntegerField()
    
    def __str__(self):
        '''Return a string representation of this model instance.'''
        return f'{self.first_name} {self.last_name} ({self.street_number} {self.street_name}), Score: {self.voter_score}'
    
    def get_full_address(self):
        '''Return the residential address.'''
        address = f'{self.street_number} {self.street_name}'
        if self.apartment_number:
            address += f', Apt {self.apartment_number}'
        address += f', {self.zip_code}'
        return address


def load_data():
    '''Function to load voter data records'''
    
    Voter.objects.all().delete()
    filename = 'voter_analytics/newton_voters.csv'
    
    try:
        f = open(filename)
        f.readline() 
        
        for line in f:
            fields = line.strip().split(',')
            
            try:
                def parse_bool(bool_str):
                    return bool_str.strip().upper() == 'TRUE'
                
                voter = Voter(
                    voter_id=fields[0],
                    last_name=fields[1],
                    first_name=fields[2],
                    street_number=fields[3],
                    street_name=fields[4],
                    apartment_number=fields[5],
                    zip_code=fields[6],
                    date_of_birth=fields[7],
                    date_of_registration=fields[8],
                    party_affiliation=fields[9].strip(),
                    precinct_number=fields[10],
                    v20state=parse_bool(fields[11]),
                    v21town=parse_bool(fields[12]),
                    v21primary=parse_bool(fields[13]),
                    v22general=parse_bool(fields[14]),
                    v23town=parse_bool(fields[15]),
                    voter_score=int(fields[16]) if fields[16] else 0,
                )
                
                voter.save()
                print(f'Created voter: {voter}')
                
            except Exception as e:
                print(f"Skipped record due to error: {fields} - Error: {e}")
        
        f.close()
        print(f'Done. Created {len(Voter.objects.all())} Voters.')
        
    except FileNotFoundError:
        print(f"File not found: {filename}")
        print("Please update the filename path in the load_data() function.")
    except Exception as e:
        print(f"Error opening file: {e}")