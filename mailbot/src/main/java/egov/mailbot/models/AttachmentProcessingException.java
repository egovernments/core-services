package egov.mailbot.models;

public class AttachmentProcessingException extends Exception {
    public AttachmentProcessingException(String errorMessage) {
        super(errorMessage);
    }
}
