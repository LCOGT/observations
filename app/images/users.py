from django.db import connections


def find_user_ids(tracknums):
    user_list = []
    for n in tracknums:
        data = tracknum_lookup(n)
        if data:
            user_list.append((n, data['proposal']['user_id']))
    return user_list


def rbauth_lookup(userlist):
    cursor = connections['rbauth'].cursor()
    sql = "select auth_user.username,userprofile.institution_name from auth_user, userprofile where auth_user.id = userprofile.user_id and auth_user.username in ('%s')" % "','".join(
        userlist)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def user_look_up(userlist):
    rows = rbauth_lookup(userlist)
    org_names = dict((x[0], x[1]) for x in rows)
    user_dict = {}
    if org_names:
        for u in userlist:
            user_dict[u] = org_names.get(u, 'Unknown')
    return user_dict


def look_up_org_names(usernames):
    ''' Parse a list of tuples mapping tracking num to username
        return a dict of tracking numbers to organization names
    '''
    if usernames:
        tracknums, userlist = zip(*usernames)
        rows = rbauth_lookup(userlist)
        org_names = dict((x[0], x[1]) for x in rows)
        user_dict = dict(usernames)
        if org_names:
            for k, v in user_dict.items():
                user_dict[k] = org_names.get(v, 'Unknown')
        return user_dict
    else:
        return {"Unknown": "Unknown"}


def collate_org_names(observations):
    ''' Small function to find the organizations of observers from a list of observations
    '''
    if observations:
        tracknums = [o['tracknum'] for o in observations]
    else:
        tracknums = []
    if tracknums:
        usernames = find_user_ids(tracknums)
        org_names = look_up_org_names(usernames)
    else:
        org_names = {"Unknown": "Unknown"}
    return org_names
