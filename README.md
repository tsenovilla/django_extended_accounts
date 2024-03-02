![CI](https://github.com/tsenovilla/django_extended_accounts/actions/workflows/tests.yaml/badge.svg)
![pre-commit](https://github.com/tsenovilla/django_extended_accounts/actions/workflows/pre-commit.yaml/badge.svg)
![Coverage](./coverage/coverage.svg)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

# Description 📖📚

**django_extended_accounts** is a Django project containing an app (**extended_accounts**) designed to extend the Django's default authentication system. As this is a common task, this project aims to be a reusable template to help developers saving a lot of time. 

This solution is based on getting rid of the Django's User model to use a custom model called AccountModel. This model is designed to only contain authentication-related information, while all personal data resides in another model called ProfileModel, which maintains a one-to-one relationship with AccountModel. The AccountModel provided is similar to the default User model in Django, with some differences:

- It does not include first and last names; these are stored in ProfileModel.
- Upon saving, it executes an additional query to save profile information in ProfileModel.
- Accounts are initially deactivated, requiring users to activate them via email after creation.

The decision behind this design is to keep the authentication model as simple as possible and avoid interference with other apps using this solution, allowing each app to specify its own user data requirements without conflicting assumptions. However, as this is just a template, you can change this design choice if you feel it's worthy of your project.

The ProfileModel contains initially the following fields: 

- First name.
- Last name.
- Phone number.
- Profile Image

Since this is a template, other fields aren't included for simplicity, but as the app is fully customizable this model may be altered to fit your project's requirements.

The provided app deals with some usual concepts present in many website accounts' system, such as:

- Allows users to upload a profile image, which is automatically converted into WebP format for efficiency while also saving the original format. If the user updates/deletes the image or the user itself is deleted, the former is automatically removed from the server.

- Sends a confirmation email to the user once it creates its account. If the account is not confirmed in an arbitrary period of time, the account is removed from the ddbb. This is achieved by integrating Celery into the project as a daemon.

Feel free to add/remove any functionality needed by your project.

##### Important Considerations ⚠️ ❗️

- Reusable apps generally shouldn't implement a custom user model as specified in [Django docs](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#reusable-apps-and-auth-user-model). However, this app is an exception as it specifically deals with extending the user model.
- Changing the authentication model mid-project is non-trivial so this app should only be used in new projects. Check [Django docs](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#changing-to-a-custom-user-model-mid-project) for further information.
- Usually, you won't interact with the ProfileModel directly but through the AccountModel. AccountModel comes with two safe methods to which you can happily pass any argument related to ProfileModel. 
These methods will automatically handle that data for you. In addition, these methods ensure the integrity of data if something goes wrong, as they rollback the database if saving to AccountModel or ProfileModel fails. 
Using other methods such as ``save`` or ``create`` may cause undesired behavior, so use them only if you're perfectly fine with them.
The safe methods are:
    
    - `create_user`: Use this method through the model manager to create a new account. Ex: ``Account.objects.create_user(username='johndoe', password='johndoe', email='johndoe@mail.com', phone_number=123456789)``

    - `update`: Use this method directly on the model instance to update an account. Ex: ``account.update(username='johndoe', phone_number=123456789, first_name='John')``


## DRF Version 📱💡

If your project uses Django Rest Framework to construct an API, the [DRF version](https://github.com/tsenovilla/django_extended_accounts_api) may be more suitable for your needs.
    

## Usage 📌🖇️

This application serves as a template for extending the Django user model. It is meant to be customized, extended, or reduced according to project requirements. Since it is not published on PyPI, the code is open for editing as needed in your project. Therefore, to use it you can follow this general guidelines:

1. Copy the application into your Django project.
2. Add specific configurations detailed at the end of `django_extended_accounts/settings.py` to your project's settings.
3. Add URLs as specified in `django_extended_accounts/urls.py`.
4. If using Celery, add `django_extended_accounts/celery.py` to the project's main folder (where `settings.py` resides).

For the sake of simplicity, this project uses development configurations in some tasks such as image uploading or email sending. For production projects, configurations should be adapted.

## Note on Celery Integration 🤝

Refer to the Celery documentation ([Celery Documentation](https://docs.celeryq.dev/en/stable/userguide/configuration.html)) for comprehensive configuration details. The included configuration is minimal for simplicity.

If you feel that your project doesn't need Celery, you can happily remove it from the template following the next steps:

- Remove Celery from the project's requirements.
- Delete Celery configurations in `django_extended_accounts/settings.py`.
- Remove `django_extended_accounts/celery.py`, `extended_accounts/helpers/tasks.py`, and `extended_accounts/signals/post_save_account_model.py` (and the related tests, of course).

## Contributing 📝

Any contribution is more than welcome! 😸🤝🦾

We use pre-commit to ensure code formatting with Black and to run code coverage, CI checks that this's been correctly done :). Please, adhere to these standards if you want to contribute.

