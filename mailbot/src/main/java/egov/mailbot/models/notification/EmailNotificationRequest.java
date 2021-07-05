package egov.mailbot.models.notification;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import org.egov.common.contract.request.RequestInfo;

@AllArgsConstructor
@NoArgsConstructor
@Builder
@Setter
@Getter
public class EmailNotificationRequest {

    private RequestInfo requestInfo = null;

    @JsonProperty("email")
    private EmailNotification email = null;
}
