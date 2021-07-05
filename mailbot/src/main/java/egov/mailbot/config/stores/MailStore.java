package egov.mailbot.config.stores;

import javax.mail.Store;

public interface MailStore {
    public Store getStore();
    public String getMailbox();
}
