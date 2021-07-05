package egov.mailbot.models.notification;

import lombok.*;

@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class InReplyTo {
    private String messageId;

    private String references;
}
