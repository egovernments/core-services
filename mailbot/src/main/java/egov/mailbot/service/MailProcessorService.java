package egov.mailbot.service;

import egov.mailbot.config.stores.MailStore;
import egov.mailbot.models.MailProcessorConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MailProcessorService {

    @Autowired
    private List<MailStore> stores;

    @Autowired
    private Map<String, MailProcessorConfig> mailConfigs = new HashMap<>();

    private Map<String, MailStore> mailStoreMap = new HashMap<>();

    @Autowired
    private MailService mailService;

    @PostConstruct
    public void init(){
        stores.forEach( m -> mailStoreMap.put(m.getMailbox(), m));
    }

    public void processMails(){
        mailStoreMap.forEach( (mailboxName, mailStore) -> {
            MailProcessorConfig config = mailConfigs.get(mailboxName);
                mailService.processMails(mailStore.getStore(), config);
        });
    }

}
