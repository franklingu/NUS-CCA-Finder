function validate(form)
{
	fail = validateForename(form.forename.value);
	fail += validateSurname(form.surname.value);
	fail += validateUsername(form.username.value);
	fail += validatePsWd(form.password.value);
	fail += validateEmail(form.email.value);

	if (fail == "")
		return true;
	else{
		alert(fail);
		return false;
	}
}

function validateForename(field)
{
	if (field == "") return "No Forename was entered\n";
	else return "";
}

function validateSurname(field)
{
	if (field == "") return "No Surname was entered\n";
	else return "";
}

function validateUsername(field)
{
	if (field == "") return "No Username was entered\n";
	else if (field.length < 5)
		return "Username must be at least 5 chars\n";
	else if (/[^a-zA-Z0-9_-]/.test(field))
		return "Only a-z,A-Z and 0-9, - , _ allowed for username\n";
	else return "";
}

function validatePsWd(field)
{
	if (field == "") return "No password was entered\n";
	else if (field.length < 6)
		return "Username must be at least 6 chars\n";
	else if (/[^a-zA-Z0-9_-]/.test(field))
		return "Only a-z,A-Z and 0-9, - , _ allowed for password\n";
	else return "";
}

function validateEmail(field)
{
	if (field == "") return "No email was entered\n";
	else if (!(field.indexOf(".")>0 && field.indexOf("@")>0 && /[^a-zA-Z0-9_-@]/.test(field)))
		return "The email is invalid\n";
	else return "";
}