package egov.mailbot.models.notification;

import lombok.*;

@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class Attachment {
    private String tenantId;

    private String fileStoreId;
}
