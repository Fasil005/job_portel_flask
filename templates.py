from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask import render_template, make_response, request, session
from models import Skills, Jobs, AppliedJobs


class LoginPage(Resource):
    def get(self):
        return make_response(render_template('login.html', data={'login_page': True}), 200)


class RegisterPage(Resource):
    def get(self):
        if request.args.get('user'):
            return make_response(render_template('register.html', data={'user': True, 'company': False, 'login_page': True}))
        return make_response(render_template('register.html', data={'user': False, 'company': True, 'login_page': True}), 200)


class ErrorPage(Resource):
    def get(self):
        return make_response(render_template('error.html', data={'login_page': True}), 200)


class HomePageJobSeeker(Resource):

    def get(self):
        jobs = Jobs.query.all()
        user_id = request.args.get('user_id')
        applied_jobs = AppliedJobs.query.filter_by(user_id=user_id).all()
        applied_jobs = [job.job_id for job in applied_jobs]
        return make_response(render_template(
            'home_job_seeker.html',
            data={
                'login_page': False
            },
            user_id=user_id,
            jobs=jobs,
            applied_jobs=applied_jobs
        ), 200)


class HomePageCompanyAdmin(Resource):

    def get(self):
        company_id = request.args.get('company_id')
        user_id = request.args.get('user_id')
        print(company_id, user_id)
        jobs = Jobs.query.filter(Jobs.company_id == company_id).order_by(Jobs.id.desc()).all()
        requirements = Skills.query.all()
        return make_response(render_template(
            'home_admin_company.html',
            data={
                'login_page': False,
                'requirements': requirements,
                'jobs': jobs,
                'company': company_id,
                'user': user_id
            }), 200)

