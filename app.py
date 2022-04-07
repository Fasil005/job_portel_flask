from models import app
from flask_restful import Api
from templates import LoginPage, RegisterPage, ErrorPage, HomePageJobSeeker, HomePageCompanyAdmin
from users import UserManagement, CompanyManagement, LoginManagement, JobManagement, JobSingleManagement, JobApply, AppliedJobsCompanyView, SearchJob, Logout

api = Api(app)

api.add_resource(LoginPage, '/')
api.add_resource(ErrorPage, '/error')
api.add_resource(RegisterPage, '/register_page')
api.add_resource(UserManagement, '/user_registering')
api.add_resource(CompanyManagement, '/company_registering')
api.add_resource(LoginManagement, '/loging_in')
api.add_resource(HomePageJobSeeker, '/home/job_seeker')
api.add_resource(HomePageCompanyAdmin, '/home/company/admin')
api.add_resource(JobManagement, '/home/company/admin/job/add')
api.add_resource(JobSingleManagement, '/home/company/admin/job/update/<pk>')
api.add_resource(JobApply, '/home/company/user/job/apply')
api.add_resource(AppliedJobsCompanyView, '/home/company/job/applied/users')
api.add_resource(SearchJob, '/home/job/users/search')
api.add_resource(Logout, '/log_out')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
