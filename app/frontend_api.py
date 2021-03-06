import config
from model import Person
import photo
from search.searcher import Searcher
import simplejson
import utils


class FrontendApiHandler(utils.BaseHandler):
    """Base handler for frontend API handlers."""

    def _return_json(self, data):
        self.response.headers['Content-Type'] = (
            'application/json; charset=utf-8')
        self.write(simplejson.dumps(data))


class Repo(FrontendApiHandler):

    repo_required = False

    def get(self):
        # TODO: implement this for real
        if self.env.repo:
            json = {
                'repoId': 'haiti',
                'title': 'Haiti earthquake',
                'recordCount': 12345
            }
        else:
            json = [
                {
                    'repoId': 'haiti',
                    'title': 'Haiti earthquake',
                    'recordCount': 12345,
                },
                {
                    'repoId': 'japan',
                    'title': 'Japan earthquake',
                    'recordCount': 54321,
                },
            ]
        self._return_json(json)


class Results(FrontendApiHandler):

    repo_required = True

    MAX_RESULTS = 100

    def _result_to_dict(self, person):
        # TODO: implement this
        return {
            'personId': person.record_id,
            'name': 'Hardcoded name',
        }

    def get(self):
        searcher = Searcher(
            self.repo, self.config.external_search_backends,
            config.get('enable_fulltext_search'), Results.MAX_RESULTS)
        results = searcher.search(
            self.params.query_name or self.params.query)
        self._return_json([self._result_to_dict(r) for r in results])


class Person(FrontendApiHandler):

    repo_required = True

    def get(self):
        # TODO: implement this
        self._return_json({'name': 'Hard-coded placeholder'})


class Create(FrontendApiHandler):

    repo_required = True

    def post(self):
        # TODO: factor all this out somewhere shared
        person = Person.create_original(
            self.repo,
            entry_date=utils.get_utcnow(),
            family_name=self.params.family_name,
            given_name=self.params.given_name,
            age=self.params.age,
            sex=self.params.sex,
            home_street=self.params.home_street,
            home_city=self.params.home_city,
            home_state=self.params.home_state,
            home_country=self.params.home_country,
        )
        if self.params.photo:
            p, photo_url = photo.create_photo(self.params.photo, self)
            p.put()
            person.photo = p
            person.photo_url = photo_url
        person.update_index(['old', 'new'])
        person.put_new()
        json = {'personId': person.record_id}
        self._return_json(json)
