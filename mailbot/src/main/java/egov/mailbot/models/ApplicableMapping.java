package egov.mailbot.models;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.egov.common.contract.request.RequestInfo;

@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
public class ApplicableMapping {
    private Mapping mapping;
    private RequestInfo requestInfo;
}
