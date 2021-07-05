package egov.mailbot.config.stores;

import lombok.extern.slf4j.Slf4j;
import org.egov.tracer.model.CustomException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.mail.MessagingException;
import javax.mail.Session;
import javax.mail.Store;
import java.util.Properties;

@Component
@Slf4j
public class HomeIsolationStore implements MailStore {

    private String username;

    private String password;

    private final Store store;

    public HomeIsolationStore(@Value("${store.home.isolation.username}") String username,
                              @Value("${store.home.isolation.password}") String password,
                              @Value("${store.home.isolation.host}") String host,
                              @Value("${store.home.isolation.port}") String port) {
        this.username = username;
        this.password = password;

        Properties properties = new Properties();
        properties.setProperty("mail.store.protocol", "imaps");
        properties.setProperty("mail.imaps.host", host);
        properties.setProperty("mail.imaps.port", String.valueOf(port));
        properties.setProperty("mail.imaps.auth", "true");
        properties.setProperty("mail.imaps.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
//            properties.setProperty("mail.imaps.ssl.trust", "*");

        try {
            // Get the session
            Session session = Session.getInstance(properties, null);
            this.store = session.getStore("imaps");
            this.store.connect(username, password);
        } catch (MessagingException e) {
            log.error("Failed to initialize mailstore, "+getMailbox(), e);
            throw new CustomException("STORE_INITIALIZATION_FAILED", "Failed to initialize mail store");
        }
    }

    @Override
    public Store getStore()  {
        try {
            if(!this.store.isConnected())
                this.store.connect(username, password);

            return this.store;

        }catch (MessagingException e){
            log.error("Failed to establish connection to mailstore, "+getMailbox(), e);
            throw new CustomException("STORE_CONNECTION_FAILED", "Failed to establish connection to mailstore");
        }
    }

    @Override
    public String getMailbox() {
        return this.username;
    }
}
