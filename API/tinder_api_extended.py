import os
import oyaml as yaml
import requests
import json
from robobrowser import RoboBrowser
from datetime import date, datetime
from random import random
from time import sleep
from GUI.log import log
import utils
from API import fb_auth_token

class TinderApi():
    def __init__(self, data_folder):
        self.get_headers = {
            'app_version': '6.9.4',
            'platform': 'ios',
            "User-agent": "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)",
            "Accept": "application/json"
        }

        self.headers = self.get_headers.copy()
        self.headers['content-type'] = "application/json"
        self.host = "https://api.gotinder.com"
        self.browser = RoboBrowser()
        self.data_folder = data_folder

    def get_person_data(self, data):
        if "user" in data:
            person = data['user']
            type = "recommendation"
        elif 'person' in data:
            person = data['person']
            type = "match"
        else:
            person = data
            type = "person"

        return person, type
    def download_people_data_api(self, data_list, folder_path, rename_images, amount, force_overwrite=False, log_to_widget=True, thread_update_signal=None):
        downloaded_data = None
        if not isinstance(data_list, list):
            data_list = [data_list]
        total = len(data_list)
        total_skipped = 0
        if amount > 0:
            total = min(total, amount)
        for i in range(total):
            if thread_update_signal is not None:
                thread_update_signal.emit("Downloading " +str(folder_path) +": " +str(i+1) + "/" + str(total) + " Skipped: " +str(total_skipped))
            log.i("API", "Downloading " + str(i + 1) + "/" + str(total), log_to_widget)
            updated_data = self.download_person_data(folder_path, data_list[i], rename_images, force_overwrite, log_to_widget)
            if updated_data is None:
                total_skipped += 1
            else:
                if downloaded_data is None:
                    downloaded_data = []
                downloaded_data.append(updated_data)
            log.i("API", "Data Downloaded!  Total Skipped: " + str(total_skipped), log_to_widget)
        return downloaded_data

    def download_person_data(self, base_folder, data, rename_images, force_overwrite=False, log_to_widget=True, thread_update_signal=None):
        log.d("API", "download_person_data: " + base_folder, log_to_widget)
        person_data, type = self.get_person_data(data)
        log.d("API", type+ " data: " + str(data.keys()), log_to_widget)
        id = person_data['_id']
        name = person_data['name']
        log.i("API", "Downloading :" +type+": " + name + " " + id, log_to_widget)
        path = base_folder+"/"+str(name)+"_"+str(id)+"/"
        person_data['path'] = str(os.path.abspath(path))
        log.d("API", "person path: " + person_data['path'], log_to_widget)
        keys = person_data.keys()
        to_download = ""
        if 'instagram' in keys:
            to_download = to_download + 'instagram'
            if 'photos' in person_data['instagram'].keys():
                to_download = to_download + '['+ str(len(person_data['instagram']['photos'])) +']'
            else:
                log.d("API", "no instagram photos", log_to_widget)
        else:
            log.d("API", "no instagram", log_to_widget)

        to_download = to_download + ' + '
        if 'photos' in keys:
            to_download = to_download + 'photos' + '['+ str(len(person_data['photos'])) +']'
        else:
            log.d("API", "no photos", log_to_widget)
        log.i("API", to_download, log_to_widget)

        if os.path.exists(path):
            log.i("API", "Already there", log_to_widget)
        else:
            os.makedirs(path)
        person_data['local_path'] = str(os.path.abspath(path))
        log.d("API", "person path created", log_to_widget)

        if 'insta' in to_download:
            self.download_instagram_photos(person_data['instagram'], path, rename_images, force_overwrite, log_to_widget)

        if 'photo' in to_download:
            self.download_photos(person_data['photos'], path, rename_images, force_overwrite, log_to_widget)

        self.download_metadata(data, path)
        return data
        # list_to_update.append(person_data)
        # return False

    def download_metadata(self, data, base_path):
        with open(base_path+'data.yaml', 'w') as fp:
            yaml.dump(data, fp)

    def download_photos(self, photos_list, base_path, rename, force_overwrite=False, log_to_widget=True, thread_update_signal=None):
        for i in range(len(photos_list)):
            photo = photos_list[i]
            filename, skipped = self.download_file(photo['url'], base_path,
                                                   rename, i, "", force_overwrite, log_to_widget)
            if not skipped:
                log.d("API", "Photo written absolute filename: "  + str(os.path.abspath(filename)), log_to_widget)
                photo['local_path']= str(os.path.abspath(filename))
            if filename is not None:
                photo['local_path'] = str(os.path.abspath(filename))
            if 'processedFiles' in photo:
                processed_files = photo['processedFiles']
                small_photo = processed_files[len(processed_files)-1]
                filename, skipped = self.download_file(small_photo['url'], base_path+"/small/",
                                                       rename, i, "_small", force_overwrite, log_to_widget=log_to_widget)
                if not skipped:
                    log.d("API", "Small Photo written filename: "  + str(os.path.abspath(filename)), log_to_widget)
                if filename is not None:
                    small_photo['local_path'] = str(os.path.abspath(filename))

    def download_instagram_photos(self, instagram_data, base_path, rename, force_overwrite=False, log_to_widget=True, thread_update_signal=None):
        if not 'photos' in instagram_data.keys():
            return
        for i in range(len(instagram_data['photos'])):
            filename, skipped = self.download_file(instagram_data['photos'][i]['image'], base_path+"instagram/",
                                                   rename, i, "", force_overwrite, log_to_widget)
            if not skipped:
                log.d("API", "Instagram photo written filename: " + str(os.path.abspath(filename)), log_to_widget)
            if filename is not None:
                instagram_data['photos'][i]['local_path'] = str(os.path.abspath(filename))

    def download_file(self, url, base_path, rename, index, postfix="", force_overwrite=False, log_to_widget=True, thread_update_signal=None):
        try:
            file_name = str(index)+postfix+".jpg"
            if not rename:
                file_name = (url.split("/")[-1] + '.jpg').split('?')[0]
            full_filename = base_path+file_name
            if not os.path.exists(base_path):
                os.makedirs(base_path)
                log.d("API", "file path created: " +base_path, log_to_widget)
            if not os.path.exists(full_filename) or force_overwrite:
                if force_overwrite:
                    log.d("API", "Forcing Re-Download: " +full_filename, log_to_widget)
                else:
                    log.i("API", "Downloading: " +full_filename, log_to_widget)
                self.browser.open(url)
                with open(full_filename, "wb") as image_file:
                    image_file.write(self.browser.response.content)
                    log.d("API", "File written: " +full_filename, log_to_widget)
                    return full_filename, False
            else:
                log.d("API", "Already Downloaded (force_overwrite=False): " +full_filename, log_to_widget)
                return full_filename, True
        except Exception as e:
            log.e("API", "EXCEPTION!: " +str(e), log_to_widget)
            return None, False

    def read_data(self, file_path, log_to_widget=True, thread_update_signal=None):
        try:
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    try:
                        data = yaml.safe_load(f)
                    except Exception as e:
                        return None
                log.i("API", "Data read from file: " + str(file_path), log_to_widget)
                return data
        except Exception as e:
            log.e("API", "Exception reading data from file : " + str(os.path.abspath(file_path)) +", Exc: " + str(e), log_to_widget)
            return None

    def reload_data_from_disk(self, folder_path, merged_filename, force_overwrite=False, log_to_widget=True, thread_update_signal=None):
        # print("log_to_widget is " +str(log_to_widget))
        # print("thread_update_signal is " +str(thread_update_signal))
        list = []
        try:
            for subdir, dirs, files in os.walk(folder_path):
                total_dirs = len(dirs)
                for i in range(len(dirs)):
                    dir = dirs[i]
                    data_path = os.path.join(subdir, dir) + "/"
                    data_file_path = data_path + "data.yaml"
                    try:
                        if os.path.exists(data_file_path):
                            with open(data_file_path) as yf:
                                data = yaml.safe_load(yf)
                                person_data, type = self.get_person_data(data)
                                person_data['local_path'] = os.path.abspath(data_path) # Updating the data path just in case
                                log.d("API", "Checking for local photos", log_to_widget)
                                if 'photos' in person_data:
                                    log.d("API", "NO local photos", log_to_widget)
                                    self.download_photos(person_data['photos'], data_path, True, force_overwrite, log_to_widget=log_to_widget)

                                log.d("API", "Checking for instagram photos", log_to_widget)
                                if 'instagram' in person_data and 'photos' in person_data['instagram']:
                                    log.d("API", "NO instagram photos", log_to_widget)
                                    self.download_instagram_photos(person_data['instagram'], data_path, True, force_overwrite, log_to_widget=log_to_widget)

                                person_data['path'] = os.path.abspath(data_path)

                                log.d("API", "Updating data file", log_to_widget)
                                self.download_metadata(person_data, data_path)
                                log.d("API", "Updated", log_to_widget)
                                list.append(data)
                            log.i("API",
                                  str(i + 1) + "/" + str(total_dirs) + " - " + str(dir) + " " + person_data['name'], log_to_widget)
                        else:
                            log.i("API", str(i + 1) + "/" + str(total_dirs) + " - " + str(dir) + " SKIPPED", log_to_widget)
                    except Exception as e:
                        log.e("API", "Exception reloading data " + str(e), log_to_widget)
                    if thread_update_signal is not None:
                        thread_update_signal.emit(str(folder_path) +"\t"+str(i + 1) + "/" + str(total_dirs))
                break
        except Exception as e:
            log.e("API", "Exception in reloading from disk: " + str(e), log_to_widget)
        try:
            with open(merged_filename, "w+") as f:
                json.dump(list, f)
        except Exception as e:
            log.e("API", "Could not save merged file " + merged_filename + ": " + str(e), log_to_widget)
        return list

    def get_fb_access_token(self, email, password, log_to_widget=True, thread_update_signal=None):
        token = fb_auth_token.get_fb_access_token(email, password)
        log.e("TOKEN", "Gotten token: " +str(token), log_to_widget)
        return token

    def get_fb_user_id(self, fb_token, log_to_widget=True, thread_update_signal=None):
        fb_id = fb_auth_token.get_fb_id(fb_token)
        log.e("FB_ID", "Gotten fb user id: " +str(fb_id), log_to_widget)
        return fb_id

    def get_auth_token(self, fb_auth_token, fb_user_id, log_to_widget=True, thread_update_signal=None):
        log.d("API", "get_auth_token: " + fb_auth_token + "\t" + fb_user_id, log_to_widget)
        if "error" in fb_auth_token:
            return {"error": "could not retrieve fb_auth_token"}
        if "error" in fb_user_id:
            return {"error": "could not retrieve fb_user_id"}
        url = self.host + '/v2/auth/login/facebook'
        req = requests.post(url,
                            headers=self.headers,
                            data=json.dumps(
                                {'token': fb_auth_token, 'facebook_id': fb_user_id})
                            )
        try:
            log.d("API", "Sending JSON request", log_to_widget)
            json_request = req.json()
            log.i("API", "Token JSON status: " +str(json_request['meta']['status']), log_to_widget)
            tinder_auth_token = json_request["data"]["api_token"]
            self.headers.update({"X-Auth-Token": tinder_auth_token})
            self.get_headers.update({"X-Auth-Token": tinder_auth_token})
            log.s("API", "You have been successfully authorized!")
            return tinder_auth_token
        except Exception as e:
            log.e("API", "Error getting Tinder Token " +str(e), log_to_widget)
            return {"error": "Something went wrong. Sorry, but we could not authorize you."}

    def authverif(self, fb_access_token, fb_user_id, log_to_widget=True, thread_update_signal=None):
        res = self.get_auth_token(fb_access_token, fb_user_id)
        if "error" in res:
            return False
        return True

    def get_recommendations(self, log_to_widget=True, thread_update_signal=None):
        '''
        Returns a list of users that you can swipe on
        '''
        try:
            r = requests.get('https://api.gotinder.com/user/recs', headers=self.headers)
            json = r.json()
            log.i("API", "get_recommendations: Got response. Status: " + str(json['status']) + ": " +utils.error_code_to_message[json['status']], log_to_widget)
            return json
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong with getting recomendations:" +str(e), log_to_widget)

    def get_updates(self, last_activity_date="", log_to_widget=True, thread_update_signal=None):
        '''
        Returns all updates since the given activity date.
        The last activity date is defaulted at the beginning of time.
        Format for last_activity_date: "2017-07-09T10:28:13.392Z"
        '''
        try:
            url = self.host + '/updates'
            r = requests.post(url,
                              headers=self.headers,
                              data=json.dumps({"last_activity_date": last_activity_date}))
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong with getting updates:" +str(e), log_to_widget)

    def get_self(self, log_to_widget=True, thread_update_signal=None):
        '''
        Returns your own profile data
        '''
        try:
            url = self.host + '/profile'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your data:" +str(e), log_to_widget)

    def change_preferences(self, **kwargs):
        '''
        ex: change_preferences(age_filter_min=30, gender=0)
        kwargs: a dictionary - whose keys become separate keyword arguments and the values become values of these arguments
        age_filter_min: 18..46
        age_filter_max: 22..55
        age_filter_min <= age_filter_max - 4
        gender: 0 == seeking males, 1 == seeking females
        distance_filter: 1..100
        discoverable: true | false
        {"photo_optimizer_enabled":false}
        '''
        try:
            url = self.host + '/profile'
            r = requests.post(url, headers=self.headers, data=json.dumps(kwargs))
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not change your preferences:" +str(e), log_to_widget)

    def get_meta(self, log_to_widget=True, thread_update_signal=None):
        '''
        Returns meta data on yourself. Including the following keys:
        ['globals', 'client_resources', 'versions', 'purchases',
        'status', 'groups', 'products', 'rating', 'tutorials',
        'travel', 'notifications', 'user']
        '''
        try:
            url = self.host + '/meta'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your metadata:" +str(e), log_to_widget)

    def get_meta_v2(self, log_to_widget=True, thread_update_signal=None):
        '''
        Returns meta data on yourself from V2 API. Including the following keys:
        ['account', 'client_resources', 'plus_screen', 'boost',
        'fast_match', 'top_picks', 'paywall', 'merchandising', 'places',
        'typing_indicator', 'profile', 'recs']
        '''
        try:
            url = self.host + '/v2/meta'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your metadata:" +str(e), log_to_widget)

    def update_location(self, lat, lon, log_to_widget=True, thread_update_signal=None):
        '''
        Updates your location to the given float inputs
        Note: Requires a passport / Tinder Plus
        '''
        try:
            url = self.host + '/passport/user/travel'
            r = requests.post(url, headers=self.headers, data=json.dumps({"lat": lat, "lon": lon}))
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not update your location:" +str(e), log_to_widget)

    def reset_real_location(self, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/passport/user/reset'
            r = requests.post(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not update your location:" +str(e), log_to_widget)

    def get_recs_v2(self, log_to_widget=True, thread_update_signal=None):
        '''
        This works more consistently then the normal get_recommendations becuase it seeems to check new location
        '''
        try:
            url = self.host + '/v2/recs/core?locale=en-US'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except Exception as e:
            log.e("API", 'excepted', log_to_widget)

    def set_webprofileusername(self, username):
        '''
        Sets the username for the webprofile: https://www.gotinder.com/@YOURUSERNAME
        '''
        try:
            url = self.host + '/profile/username'
            r = requests.put(url, headers=self.headers,
                             data=json.dumps({"username": username}))
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not set webprofile username:" +str(e), log_to_widget)

    def reset_webprofileusername(self, username):
        '''
        Resets the username for the webprofile
        '''
        try:
            url = self.host + '/profile/username'
            r = requests.delete(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not delete webprofile username:" +str(e), log_to_widget)

    def get_person(self, id, log_to_widget=True, thread_update_signal=None):
        '''
        Gets a user's profile via their id
        '''
        try:
            url = self.host + '/user/%s' % id
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get that person:" +str(e), log_to_widget)

    def send_msg(self, match_id, msg):
        try:
            url = self.host + '/user/matches/%s' % match_id
            r = requests.post(url, headers=self.headers,
                              data=json.dumps({"message": msg}))
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not send your message:" +str(e), log_to_widget)

    def unmatch(self, match_id, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/user/matches/%s' % match_id
            r = requests.delete(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not unmatch person:" +str(e), log_to_widget)

    def superlike(self, person_id, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/like/%s/super' % person_id
            r = requests.post(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not superlike:" +str(e), log_to_widget)

    def like(self, person_id, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/like/%s' % person_id
            r = requests.get(url, headers=self.get_headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not like:" +str(e), log_to_widget)

    def dislike(self, person_id, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/pass/%s' % person_id
            r = requests.get(url, headers=self.get_headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not dislike:" +str(e), log_to_widget)

    def report(self, person_id, cause, explanation='', log_to_widget=True, thread_update_signal=None):
        '''
        There are three options for cause:
            0 : Other and requires an explanation
            1 : Feels like spam and no explanation
            4 : Inappropriate Photos and no explanation
        '''
        try:
            url = self.host + '/report/%s' % person_id
            r = requests.post(url, headers=self.headers, data={
                "cause": cause, "text": explanation})
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not report:" +str(e), log_to_widget)

    def match_info(self, match_id, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/matches/%s' % match_id
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your match info:" +str(e), log_to_widget)

    def get_matches(self, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/v2/matches'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your match info:" +str(e), log_to_widget)

    def all_matches(self, amount=60, message=0, page_token=None, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/v2/matches?locale=en&count=' + str(amount) + '&message=' + str(
                message) + '&is_tinder_u=false'
            log.d("API", "All matches page: " + str(page_token), log_to_widget)
            if page_token:
                url = url + '&page_token=' + page_token
            r = requests.get(url, headers=self.headers)
            json = r.json()
            log.d("API", "All matches keys " +str(json.keys()), log_to_widget)
            log.d("API", "All matches data " +str(json['data'].keys()), log_to_widget)
            log.d("API", "All matches data matches  " + str(len(json['data']['matches'])) +" " +str(json['data']['matches'][0].keys()), log_to_widget)
            log.d("API", "All matches meta " +str(json['meta'].keys()), log_to_widget)
            log.i("API", "all_matches: Got response. Status: " + str(json['meta']['status']) + ": " +utils.error_code_to_message[json['meta']['status']], log_to_widget)
            if 'next_page_token' in json['data']:
                new_data = self.all_matches(amount, message, json['data']['next_page_token'])
                json['data']['matches'] = json['data']['matches'] + new_data['data']['matches']
            elif message <= 0:
                new_data = self.all_matches(amount, 1, None)
                json['data']['matches'] = json['data']['matches'] + new_data['data']['matches']
            log.i("API", "Total matches " + str(len(json['data']["matches"])), log_to_widget)
            return json
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your match info:" +str(e), log_to_widget)

    def fast_match_info(self, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/v2/fast-match/preview'
            r = requests.get(url, headers=self.headers)
            count = r.headers['fast-match-count']
            # image is in the response but its in hex..
            return count
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your fast-match count:" +str(e), log_to_widget)

    def trending_gifs(self, limit=3, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/giphy/trending?limit=%s' % limit
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get the trending gifs:" +str(e), log_to_widget)

    def gif_query(self, query, limit=3, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/giphy/search?limit=%s&query=%s' % (limit, query)
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your gifs:" +str(e), log_to_widget)

    # def see_friends(self, log_to_widget=True, thread_update_signal=None):
    #     try:
    #         url = self.host + '/group/friends'
    #         r = requests.get(url, headers=self.headers)
    #         return r.json()['results']
    #     except requests.exceptions.RequestException as e:
    #         log.e("API", "Something went wrong. Could not get your Facebook friends:" +str(e), log_to_widget)


    """ FEATURES """
    def get_match_info(self, log_to_widget=True, thread_update_signal=None):
        matches = self.get_updates()['matches']
        now = datetime.utcnow()
        match_info = {}
        for match in matches[:len(matches)]:
            try:
                person = match['person']
                person_id = person['_id']  # This ID for looking up person
                name = person['name']
                id = match['id']
                msg_count = match['message_count']
                photos = self.get_photos(person)
                bio = ""
                if 'bio' in person.keys():
                    bio = person['bio']
                gender = person['gender']
                avg_succ_rate = self.get_avg_successRate(person)
                messages = match['messages']
                age = self.calculate_age(match['person']['birth_date'])
                distance = self.get_person(person_id)['results']['distance_mi']
                last_activity_date = match['last_activity_date']
                match_info[person_id] = {
                    "name": name,
                    "match_id": id,  # This ID for messaging
                    "message_count": msg_count,
                    "photos": photos,
                    "bio": bio,
                    "gender": gender,
                    "avg_successRate": avg_succ_rate,
                    "messages": messages,
                    "age": age,
                    "distance": distance,
                    "last_activity_date": last_activity_date,
                }
                log.d("API", name+"_"+id)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                log.e("API", message)
                # continue
        log.i("API", "All data stored in variable: match_info")
        filename = self.data_folder + 'match_info.json'
        with open(filename, 'w') as fp:
            json.dump(match_info, fp)
            log.i("API", "All data dumped to file: " + str(os.path.abspath(filename)))
        return match_info

    def get_match_id_by_name(self, name, log_to_widget=True, thread_update_signal=None):
        '''
        Returns a list_of_ids that have the same name as your input
        '''
        global match_info
        list_of_ids = []
        for match in match_info:
            if match_info[match]['name'] == name:
                list_of_ids.append(match_info[match]['match_id'])
        if len(list_of_ids) > 0:
            return list_of_ids
        return {"error": "No matches by name of %s" % name}

    def get_photos(self, person, log_to_widget=True, thread_update_signal=None):
        '''
        Returns a list of photo urls
        '''
        photos = person['photos']
        photo_urls = []
        for photo in photos:
            photo_urls.append(photo['url'])
        return photo_urls

    def calculate_age(self, birthday_string, log_to_widget=True, thread_update_signal=None):
        '''
        Converts from '1997-03-25T22:49:41.151Z' to an integer (age)
        '''
        birthyear = int(birthday_string[:4])
        birthmonth = int(birthday_string[5:7])
        birthday = int(birthday_string[8:10])
        today = date.today()
        return today.year - birthyear - ((today.month, today.day) < (birthmonth, birthday))

    def get_avg_successRate(self, person, log_to_widget=True, thread_update_signal=None):
        '''
        SuccessRate is determined by Tinder for their 'Smart Photos' feature
        '''
        photos = person['photos']
        curr_avg = 0
        for photo in photos:
            try:
                photo_successRate = photo['successRate']
                curr_avg += photo_successRate
            except:
                return -1
        return curr_avg / len(photos)

    def sort_by_value(self, sortType, log_to_widget=True, thread_update_signal=None):
        '''
        Sort options are:
            'age', 'message_count', 'gender'
        '''
        global match_info
        return sorted(match_info.items(), key=lambda x: x[1][sortType], reverse=True)

    def see_friends(self, log_to_widget=True, thread_update_signal=None):
        try:
            url = self.host + '/group/friends'
            r = requests.get(url, headers=self.headers)
            return r.json()['results']
        except requests.exceptions.RequestException as e:
            log.e("API", "Something went wrong. Could not get your Facebook friends:" +str(e), log_to_widget)

    def see_friends_profiles(self, name=None, log_to_widget=True, thread_update_signal=None):
        friends = self.see_friends()
        if name == None:
            return friends
        else:
            result_dict = {}
            name = name.title()  # upcases first character of each word
            for friend in friends:
                if name in friend["name"]:
                    result_dict[friend["name"]] = friend
            if result_dict == {}:
                return "No friends by that name"
            return result_dict

    def convert_from_datetime(self, difference, log_to_widget=True, thread_update_signal=None):
        secs = difference.seconds
        days = difference.days
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        return ("%d days, %d hrs %02d min %02d sec" % (days, h, m, s))

    def get_last_activity_date(self, now, ping_time, log_to_widget=True, thread_update_signal=None):
        ping_time = ping_time[:len(ping_time) - 5]
        datetime_ping = datetime.strptime(ping_time, '%Y-%m-%dT%H:%M:%S')
        difference = now - datetime_ping
        since = self.convert_from_datetime(difference)
        return since

    def how_long_has_it_been(self, log_to_widget=True, thread_update_signal=None):
        global match_info
        now = datetime.utcnow()
        times = {}
        for person in match_info:
            name = match_info[person]['name']
            ping_time = match_info[person]['last_activity_date']
            since = self.get_last_activity_date(now, ping_time)
            times[name] = since
            log.i("API", name, "----->", since)
        return times

    def pause(self, log_to_widget=True, thread_update_signal=None):
        '''
        In order to appear as a real Tinder user using the app...
        When making many API calls, it is important to pause a...
        realistic amount of time between actions to not make Tinder...
        suspicious!
        '''
        nap_length = 3 * random()
        log.d("API", 'Napping for %f seconds...' % nap_length)
        sleep(nap_length)