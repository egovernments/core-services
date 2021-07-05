package egov.mailbot.models.notification;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.util.Set;

@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class EmailNotification {

    private Set<String> emailTo;
    private String subject;
    private String body;

    private Attachment attachment;

    private InReplyTo inReplyTo;

    @JsonProperty("isHTML")
    private boolean isHTML;

}
