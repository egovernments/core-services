package egov.mailbot.utils;

import com.jayway.jsonpath.JsonPath;
import egov.mailbot.models.Mapping;
import org.apache.logging.log4j.util.Strings;
import org.egov.common.contract.request.Role;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class Utils {

    //TODO Render HTML with table via mustache later
    public static String getErrorBody(List<Mapping> mappings){
        StringBuilder sb = new StringBuilder("Greetings! \nThe subject used is invalid! Please find below the " +
                "allowed operations configured for your email \n\n");

        mappings.forEach( mapping -> {
            sb.append("OPERATION: ").append(mapping.getDescription()).append("\nSUBJECTS: ").append(String.join(" OR ",
                    mapping.getSubject())).append(
                    "\n\n");
        });

        sb.append("Thanks.");
        return sb.toString();
    }

    public static String maskEmail(String email){
        if(email == null)
            return "";
        return email.replaceAll("(^[^@]{3}|(?!^)\\G)[^@]", "$1*");
    }

    public static List<String> roleCodes(List<Role> roles){
        if(roles ==null )
            return Collections.emptyList();
        return roles.stream().map(Role::getCode).collect(Collectors.toList());
    }

    public static boolean matchSubject(List<String> matchSubjects, String currSubject){
        for(String sub : matchSubjects){
            if(currSubject.toLowerCase().replaceAll("\\s","").trim().contains(sub.toLowerCase().replaceAll("\\s","")))
                return true;
        }
        return false;
    }

    public static String getErrorMessages(String json){
        if(json == null)
            return "";
        List<String> messages = JsonPath.read(json, "$.Errors[*].message");
        if(!messages.isEmpty()){
            return Strings.join(messages, ';');
        } else
            return "";
    }

    public static String enrichNotificationMessage(String errorTemplate, String error){
        if(error == null)
            return error;
        return errorTemplate.replace("${error}", error);
    }
}
