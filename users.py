from flask import request, redirect, make_response, render_template
from flask_restful import Resource
from werkzeug.utils import secure_filename
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies
from sqlalchemy import or_, func
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import SQLAlchemyError

from models import app, db, User, Company, Skills, Jobs, AppliedJobs
from utils import login_required
import os


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']


class UserManagement(Resource):

    def post(self):
        try:
            data = request.form
            file = request.files
            if allowed_file(file['image'].filename):
                filename = secure_filename(file['image'].filename)
                file['image'].save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user = User(
                    username=data.get('username'),
                    email=data.get('email'),
                    password=data.get('password'),
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    phone_number=data.get('phone_number'),
                    qualification=data.get('qualification'),
                    photo=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                )
                for item in data.get('skills').split(','):
                    if Skills.query.filter_by(name=item).count() > 0:
                        user.skills.append(
                            Skills.query.filter_by(name=item).first()
                        )

                    else:
                        skill = Skills(name=item)
                        db.session.add(skill)
                        db.session.commit()
                        user.skills.append(skill)
                db.session.add(user)
                db.session.commit()
                return redirect('/')
            else:
                return redirect('/register_page?user=True')
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class CompanyManagement(Resource):

    def post(self):
        try:
            data = request.form
            company = Company(
                name=data.get('name'),
            )
            db.session.add(company)
            db.session.commit()
            user = User(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                company_id=company.id,
                is_admin=True,
            )
            db.session.add(user)
            db.session.commit()
            hiring_for = data.get('hiring_for')
            for item in hiring_for.split(','):
                if Skills.query.filter_by(name=item).count() > 0:
                    pass

                else:
                    skill = Skills(name=item)
                    db.session.add(skill)
                    db.session.commit()
            return redirect('/')
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class LoginManagement(Resource):

    def post(self):
        try:
            data = request.form
            user = User.query.filter(or_(User.email == data.get('email_username'), User.username == data.get('email_username'))).first()
            if user and user.password == data.get('password'):
                access_token = create_access_token(identity=user.id)

                if user.is_admin:
                    resp = redirect('/home/company/admin?company_id=' + str(user.company_id) + '&user_id=' + str(user.id))
                    set_access_cookies(resp, access_token)
                    return resp
                resp = redirect('/home/job_seeker?user_id=' + str(user.id))
                set_access_cookies(resp, access_token)
                return resp
            else:
                return redirect('/')
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class JobManagement(Resource):

    @login_required
    def post(self):
        try:
            data = request.form
            print(data)
            job = Jobs(
                job_title=data.get('job_title'),
                job_description=data.get('job_description'),
                job_location=data.get('job_location'),
                job_salary=data.get('job_salary'),
                company_id=data.get('company_id'),
                user_id=data.get('user_id'),
                job_requirements=data.get('job_requirements'),
            )
            job_skills = str(data.get('job_skills'))

            for item in job_skills.split(','):
                if Skills.query.filter_by(name=item).count() > 0:
                    job.skills.append(
                        Skills.query.filter_by(name=item).first()
                    )

                else:
                    skill = Skills(name=item)
                    db.session.add(skill)
                    db.session.commit()
                    job.skills.append(skill)
            db.session.add(job)
            db.session.commit()

            return redirect('/home/company/admin?company_id=' + str(data.get('company_id')) + '&user_id=' + str(data.get('user_id')))
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class JobSingleManagement(Resource):

    @login_required
    def get(self, pk):
        try:
            job = Jobs.query.filter_by(id=pk).first()
            delete = request.args.get('delete')
            if delete:
                db.session.delete(job)
                db.session.commit()
                return redirect('/home/company/admin?company_id=' + str(job.company_id) + '&user_id=' + str(job.user_id))

            jobs = Jobs.query.filter_by(company_id=job.company_id).order_by(Jobs.id.desc()).all()
            requirements = Skills.query.all()
            return make_response(render_template(
                'home_admin_company.html',
                data={
                    'login_page': False,
                    'requirements': requirements,
                    'jobs': jobs,
                },
                job=job
            ), 200)
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')

    @login_required
    def post(self, pk):

        try:
            data = request.form
            job = Jobs.query.filter_by(id=pk).first()
            job.job_title = data.get('job_title')
            job.job_description = data.get('job_description')
            job.job_location = data.get('job_location')
            job.job_salary = data.get('job_salary')
            job.job_requirements = data.get('job_requirements')

            db.session.commit()
            return redirect('/home/company/admin?company_id=' + str(job.company_id) + '&user_id=' + str(job.user_id))
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class JobApply(Resource):

    @login_required
    def get(self):
        try:
            app_job = AppliedJobs(
                job_id=request.args.get('job_id'),
                user_id=request.args.get('user_id')
            )
            db.session.add(app_job)
            db.session.commit()
            return redirect('/home/job_seeker?user_id=' + str(request.args.get('user_id')))
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class AppliedJobsCompanyView(Resource):

    @login_required
    def get(self):
        try:
            company_id = request.args.get('company_id')
            jobs = Jobs.query.filter_by(company_id=company_id).all()
            response = []
            for job in jobs:
                response += AppliedJobs.query.filter_by(job_id=job.id).all()
            return make_response(render_template(
                'home_job_seeker.html',
                data={
                    'login_page': False,
                    'non_searchable': True
                },
                response=response
            ), 200)
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class SearchJob(Resource):

    @login_required
    def post(self):
        try:
            data = request.form
            search_keyword = data.get('keyword')
            jobs = Jobs.query.filter(or_(
                func.lower(Jobs.job_title).like(f'%{search_keyword.lower()}%'),
                func.lower(Jobs.job_description).like(f'%{search_keyword.lower()}%'),
                func.lower(Jobs.job_location).like(f'%{search_keyword.lower()}%'),
                func.lower(Jobs.job_salary).like(f'%{search_keyword.lower()}%')
            )).all()

            user_id = request.args.get('user_id')
            applied_jobs = AppliedJobs.query.filter_by(user_id=user_id).all()
            applied_jobs = [job.job_id for job in applied_jobs]
            return make_response(render_template(
                'home_job_seeker.html',
                data={
                    'login_page': False,
                },
                user_id=user_id,
                jobs=jobs,
                applied_jobs=applied_jobs
            ), 200)
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')


class Logout(Resource):

    @login_required
    def get(self):
        try:
            resp = make_response(render_template(
                'login.html',
                data={
                    'login_page': True,
                }
            ), 200)
            unset_jwt_cookies(resp)
            return resp
        except SQLAlchemyError as e:
            print(e)
            return redirect('/error')
        except Exception as e:
            print(e)
            return redirect('/error')
