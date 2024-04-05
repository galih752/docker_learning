#User
def UserPramuka(item)->dict:
    return {
        "id":str(item["_id"]),
        "full_name":item["full_name"],
        "username":item["username"],
        "email":item["email"],
        "active":item["active"],
    }
    
def UsersPramuka(entity)->list:
    return [UserPramuka(item)for item in entity]

#Activity
def ActivityPramuka(item)->dict:
    return {
        "id":str(item["_id"]),
        "activity_name":item["activity_name"],
        "circular_letter":item["circular_letter"],
        "participant_requirements":item["participant_requirements"],
        "schedule_of_activities":item["schedule_of_activities"]
    }
    
def ActivitiesPramuka(entity)->list:
    return [ActivityPramuka(item)for item in entity]

#Data Potensi
def DataPotensi(item:dict)-> dict:
    return {
        "id": str(item["_id"]),
        "gudep": item.get("gudep", None),
        "male_builder": item.get("male_builder", None),
        "female_builder": item.get("female_builder", None),
        "male_member": item.get("male_member", None),
        "female_member": item.get("female_member", None),
        "bantara_member": item.get("bantara_member", None),
        "laksana_member": item.get("laksana_member", None),
        "garuda_member": item.get("garuda_member", None),
    }
    
def DatasPotensi(entity)->list:
    return [DataPotensi(item)for item in entity]

#Dewan Kerja Ranting
def DewanKerja(item)->dict:
    return {
        "id":str(item["_id"]),
        "name":item["name"],
        "school_name":item["school_name"],
        "level":item["level"],
        "position":item["position"],
        "period":item["period"],
        "status":item["status"],
    }
    
def DewansKerja(entity)->list:
    return [DewanKerja(item)for item in entity]

#News
def NewPramuka(item) -> dict:
    return {
        "_id": str(item["_id"]),
        "title": item["title"],
        "description": item["description"],
        "content": item["content"],
        "hashtag": item["hashtag"],
        "thumbnail": item.get("thumbnail"),
        "author": item.get("author"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "comments": item.get("comments"),
    }
def NewsPramuka(entity)->list:
    return [NewPramuka(item)for item in entity]

#Comments
def NewsComentItem(item) -> dict:
        return {
            "id": str(item.get("_id", "")),
            "sender_name":item.get("sender_name",""),
            "content": item["content"],
            "id_news": item["id_news"],
            "created_at": item["created_at"].isoformat() if "created_at" in item else ""
        }

def NewsComents(entity)->list:
    return [NewsComentItem(item)for item in entity]

#Opinion
def OpinionPramuka(item)->dict:
    return {
        "id":str(item["_id"]),
        "sender_name":item["sender_name"],
        "subject":item["subject"],
        "content":item["content"],
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }
    
def OpinionsPramuka(entity)->list:
    return [OpinionPramuka(item)for item in entity]


#School in Padalarang
def SchoolPadalarang(item)->dict:
    return {
        "id":str(item["_id"]),
        "school_name":item["school_name"],
        "ambalan_name":item["ambalan_name"],
        "level":item["level"],
        "gudep":item["gudep"],
        "registration":item["registration"],
    }
def SchoolsPadalarang(entity)->list:
    return[SchoolPadalarang(item)for item in entity]