package egov.mailbot.service;

import egov.mailbot.models.Action;
import egov.mailbot.models.AttachmentProcessingException;
import egov.mailbot.models.Mapping;
import egov.mailbot.models.notification.EmailNotificationRequest;

import java.nio.file.Path;

public interface AttachmentProcessor {
    public void processAttachments(EmailNotificationRequest notificationRequest, Mapping mapping, Path path) throws AttachmentProcessingException;
    public Action action();

}

