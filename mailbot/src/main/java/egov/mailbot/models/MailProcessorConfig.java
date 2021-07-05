package egov.mailbot.models;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.util.List;
import java.util.Set;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class MailProcessorConfig {


    @JsonProperty("service")
    private String service = null;

    @JsonProperty("mailbox")
    private String mailbox = null;

    @JsonProperty("mappings")
    private List<Mapping> mappings = null;

    @JsonIgnore
    private Set<String> tenantIds = null;
}
