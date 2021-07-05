package egov.mailbot.controllers;

import egov.mailbot.service.MailProcessorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MailProcessorController {

    @Autowired
    private MailProcessorService mailProcessorService;

    @RequestMapping(value = "/_process", method = RequestMethod.GET)
    public ResponseEntity<Void> upload( ){
        mailProcessorService.processMails();

        return new ResponseEntity<Void>(HttpStatus.OK);
    }

}
