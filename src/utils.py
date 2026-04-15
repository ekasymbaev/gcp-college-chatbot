def build_user_info(first_name, last_name, email):
    return {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip()
    }


def validate_user_info(user_info):
    errors = {}

    if not user_info["first_name"]:
        errors["first_name"] = "First name is required"
    if not user_info["last_name"]:
        errors["last_name"] = "Last name is required"
    if not user_info["email"]:
        errors["email"] = "Email is required"

    return errors